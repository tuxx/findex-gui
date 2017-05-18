#!/usr/bin/pypy3
"""
Usage: script.py

Enjoy this unmaintainable piece of spaghetti! It parses
the IDMB plain text files over at http://imdb.com/interfaces.

Takes about 20 minutes on my pc.

Requirements:
- needs to be run through pypy3 (not cPython)
- 4GB RAM or higher (may lock up your pc)

Steps this script takes:
1) download & unpack files
2) parse files
3) generate SQL
4) execute SQL

Affected Postgres tables are:
- meta_imdb
- meta_imdb_actors
- meta_imdb_directors
- files

Required IMDB data files
- actors.list
- actresses.list
- directors.list
- genres.list
- plot.list
- ratings.list

Warning: Don't hook this up to user input
"""
from datetime import datetime
import sys
import os
import copy
import re
import subprocess
import gzip
import json

import settings


TMP_FOLDER = None
IMDB_ENCODING = "ISO-8859-1"
CREDS = {"db_host": settings.db_hosts[0], "db_port": settings.db_port, "db_name": settings.db_name,
         "db_user": settings.db_user, "db_pass": settings.db_pass}
cwd = os.path.dirname(os.path.abspath(__file__))


def read_data_file(filename=None, start_from=None, filepath=None):
    global TMP_FOLDER
    if filepath:
        filename = filepath
    else:
        filename = "%s%s.list" % (TMP_FOLDER, filename)

    print("loading: %s" % filename)
    f = open(filename, "r", encoding=IMDB_ENCODING)
    data = f.read()
    f.close()

    if start_from:
        data = data[data.find(start_from):]
    data = data.split("\n")[1:]
    return data


def read_data_file_chunks(filename, chunk=0):
    global TMP_FOLDER
    filename = "%s%s.list" % (TMP_FOLDER, filename)
    max_bytes = 128598041

    print("loading: %s, chunk: %d" % (filename, chunk))
    f = open(filename, "r", encoding=IMDB_ENCODING)
    f.seek(max_bytes*chunk)
    data = f.read(max_bytes)
    f.close()
    if not data:
        return
    else:
        data = data.split("\n")[1:]
        return data


def parse_remaining(line, exclude_formats="VG"):
    if not line:
        return

    rtn = {}
    if not isinstance(exclude_formats, list):
        exclude_formats = exclude_formats.split(",")
    line = line.strip()
    if line.endswith("}"):
        return

    while line.endswith(")"):  # search from the right till all the () are gone
        pos = line.rfind("(")
        last_crap = line[pos:][1:-1]

        _continue = False
        for remove in ["V", "TV", "VG"]:
            if last_crap == remove:
                if last_crap in exclude_formats:
                    return
                line = line[:-len(remove)-2].strip()
                _continue = True
        if _continue:
            continue

        # detected year
        if len(last_crap) >= 4 and last_crap[:4].isdigit():
            rtn["year"] = int(last_crap[:4])
            line = line[:-len(last_crap) - 2].strip()
        else:
            # detected crap, remove
            line = line[:-len(last_crap)-2].strip()
            continue

    if not rtn.get("year") or not line:
        return

    if "\"" in line:
        line = line[line.find("\"") + 1:]
        _lq = line.rfind("\"")
        rtn["title"] = line[:_lq].strip()
    else:
        rtn["title"] = line.strip()

    return rtn["title"], rtn["year"]


def parse_name(inp):
    inp = inp.strip()
    if "," in inp:
        last_crap = ""
        if inp.endswith(")") and "(" in inp:
            _s = inp.rfind("(")
            last_crap = " " + inp[_s:]
            inp = inp[:_s-1]
        spl = inp.split(",", 1)
        inp = "%s %s%s" % (spl[1], spl[0], last_crap)
        return inp.strip()
    return inp


class ToSql:
    def __init__(self, ratings):
        self._now = datetime.now().strftime("%Y-%m-%d-%H-%M")
        self._ratings = ratings

    def __call__(self):
        actors = self.actors()
        directors = self.directors()
        ratings = self.ratings()

        return {
            "directors": directors,
            "ratings": ratings,
            "actors": actors
        }

    def actors(self):
        """
        CREATE TABLE meta_imdb_actors (
            id SERIAL8 NOT NULL PRIMARY KEY,
            actor fulltext NOT NULL
        );

        CREATE INDEX idx_zdb_imdb_actors
            ON meta_imdb_actors
        USING zombodb(zdb('meta_imdb_actors', meta_imdb_actors.ctid), zdb(meta_imdb_actors))
        WITH (url='http://localhost:9200/');

        DELETE FROM meta_actors;
        COPY meta_imdb_actors FROM 'path';
        """
        out_file = "%sfindex_imdb-%s-actors.sql" % (TMP_FOLDER, self._now)
        f = open(out_file, "w", encoding="UTF-8")

        actors = []
        for rating in self._ratings.ratings:
            _actors = rating.get("actors", [])
            for _actor in _actors:
                if _actor not in actors and _actor:
                    actors.append(_actor)
        for i, actor in enumerate(actors):
            f.write("%d\t%s\n" % (i, ToSql.latin_to_unicode(actor)))
        f.close()
        return out_file

    def directors(self):
        """
        CREATE TABLE meta_imdb_directors (
            id SERIAL8 NOT NULL PRIMARY KEY,
            actor fulltext NOT NULL
        );

        CREATE INDEX idx_zdb_imdb_directors
            ON meta_imdb_directors
        USING zombodb(zdb('meta_imdb_directors', meta_imdb_directors.ctid), zdb(meta_imdb_directors))
        WITH (url='http://localhost:9200/');

        DELETE FROM meta_imdb_directors;
        COPY meta_imdb_directors FROM 'path';
        """
        global TMP_FOLDER
        out_file = "%sfindex_imdb-%s-directors.sql" % (TMP_FOLDER, self._now)
        f = open(out_file, "w", encoding="UTF-8")

        directors = []
        for rating in self._ratings.ratings:
            _director = rating.get("director")
            if _director and _director not in directors:
                directors.append(_director)

        for i, director in enumerate(directors):
            f.write("%d\t%s\n" % (i, ToSql.latin_to_unicode(director)))
        f.close()
        return out_file

    def ratings(self):
        """
        CREATE TABLE meta_imdb (
            id SERIAL8 NOT NULL PRIMARY KEY,
            title fulltext NOT NULL,
            year SMALLINT NOT NULL,
            rating SMALLINT NOT NULL,
            director fulltext,
            genres VARCHAR(32)[],
            actors VARCHAR(64)[],
            plot phrase
        );

        CREATE INDEX idx_zdb_imdb
            ON meta_imdb
        USING zombodb(zdb('meta_imdb', meta_imdb.ctid), zdb(meta_imdb))
        WITH (url='http://localhost:9200/');

        DELETE FROM meta_imdb;
        COPY meta_imdb FROM 'path';
        """
        global TMP_FOLDER
        out_file = "%sfindex_imdb-%s-ratings.sql" % (TMP_FOLDER, self._now)
        f = open(out_file, "w", encoding="UTF-8")

        for i, rating in enumerate(self._ratings.ratings):
            _actors = ToSql.make_array(rating.get("actors", []), limit=63)
            _director = ToSql.sanitize(rating.get("director", "NULL"))
            _genres = ToSql.make_array(rating.get("genres", []), limit=31)
            _rating = rating.get("rank", -1)
            _title = ToSql.sanitize(rating.get("title", ""))
            if not _title:
                continue

            _year = rating.get("year")
            if not _year:
                continue

            _plot = rating.get("plot")
            sql = "%d\t%s\t%d\t%d\t%s\t%s\t%s\t%s" % (i, _title, _year, _rating, _director, _genres, _actors, _plot)
            f.write("%s\n" % sql)
        f.close()
        return out_file

    @staticmethod
    def sanitize(inp, limit=None):
        if isinstance(inp, str) and inp != "NULL":
            if limit:
                inp = inp[:limit]
            inp = inp \
                .encode("UTF-8", 'unicode_escape') \
                .decode("utf-8").replace("\t", "\\\t")
        return inp

    @staticmethod
    def make_array(arr, limit=None):
        _items = []
        for _a in arr:
            if not _a:
                _a = "NULL"
            elif isinstance(_a, str):
                _a = ToSql.sanitize(_a, limit)
                _a = _a.replace(",", "\,")
            elif isinstance(_a, (int, float)):
                _a = str(_a)
            _items.append(_a)
        if _items:
            return "{%s}" % ",".join(_items)
        else:
            return "{}"

    @staticmethod
    def latin_to_unicode(inp):
        return inp.encode("UTF-8", 'unicode_escape').decode("utf-8").replace("\t", "\\\t")


class RatingsResult:
    def __init__(self, ratings):
        self.ratings = ratings
        self.lookups = []
        self.fast_lookups()

    def fast_lookups(self):
        for rating in self.ratings:
            self.lookups.append(rating["title"])


class Ratings:
    @staticmethod
    def get(min_rank=None, min_votes=15000, min_year=1960,
            exclude_formats="VG", debug_max_lines=-1,
            include_genres=True):
        """
        "xxxxx"        = a television series
        "xxxxx" (mini) = a television mini-series
        (TV)           = TV movie, or made for cable movie
        (V)            = made for video movie (this category does NOT include TV
                         episodes repackaged for video, guest appearances in
                         variety/comedy specials released on video, or
                         self-help/physical fitness videos)
        (VG)           = video game

        :param min_rank: filter minimum rating
        :param min_votes: filter minimum amount of votes
        :param min_year: filter earliest year
        :param exclude_formats: comma delimited, VG:videogames
        :return: str: title rank year, \t delimited
        """
        data = []
        exclude_formats = exclude_formats.split(",")
        lines = read_data_file("ratings", "#140Characters: A Documentary About Twitter (2011)")

        if include_genres:
            genres = read_data_file("genres", "THE GENRES LIST")
            genres = genres[2:]
            genre_list = {}
            print("Parsing genres. Estimated: 5 - 30 seconds")
            for genre in genres:
                if not genre or "\t" not in genre:
                    continue

                if "{" in genre:
                    continue

                genre = genre.replace("\"", "")
                title = genre[:genre.find("\t")]
                genre = genre[genre.rfind("\t") + 1:]

                if "-" in genre and genre != "Sci-Fi":
                    continue

                if title[0] not in genre_list:
                    genre_list[title[0]] = []

                genre_list[title[0]].append({"title": title, "genre": genre})

        def get_genre(title, year):
            return [z["genre"] for z in genre_list[title[0]] if z["title"].startswith("%s (%d)" % (title, year))]

        print("Parsing ratings. Estimated: 10 - 60 seconds")
        i = 0
        for line in lines:
            if not line:
                continue

            if line.startswith("-"):
                break

            if line.endswith("}"):
                continue

            if line.count(" ") < 4:
                continue

            _line = [z for z in line.split(" ") if z]
            distribution, votes, rank = _line[:3]
            if not votes.isdigit() or "." not in rank:
                raise Exception("not digit")

            votes = int(votes)
            rank = int(float(rank)*10)

            if votes < min_votes:
                continue

            if min_rank:
                if rank < min_rank:
                    continue

            remaining = " ".join(_line[3:])
            remaining = parse_remaining(remaining, exclude_formats=exclude_formats)
            if not remaining:
                continue

            title, year = remaining

            if min_year:
                if year < min_year:
                    continue

            if include_genres:
                genres = get_genre(title, year)
            else:
                genres = []

            data.append({"title": title, "rank": rank, "year": year, "genres": genres})
            i += 1

            if debug_max_lines > 0:
                if i > debug_max_lines:
                    break

        if debug_max_lines >= 5000:
            if len(data) < 5000:
                raise Exception("Should be higher than 5000 "
                                "perhaps IMDB changed data")

        rtn = RatingsResult(data)
        return rtn


class Directors:
    @staticmethod
    def get(ratings, exclude_formats="VG"):
        lines = read_data_file("directors", "THE DIRECTORS LIST")
        lines = lines[4:]

        x = [z.replace("\"", "") for z in "\n".join(lines).split("\t") if z]

        print("Parsing directors: Estimated: 5 - 10min")
        for rating in ratings.ratings:
            z = "%s (%d" % (rating["title"], rating["year"])

            res = [w for w in x if w.startswith(z)]
            if res:
                res = res[0]
                start_pos = x.index(res)
                end_pos = -1
                while "\n\n" not in x[start_pos]:
                    start_pos -= 1
                    end_pos = start_pos + 1

                while "\n\n" not in x[end_pos]:
                    end_pos += 1

                content = x[start_pos:][:end_pos + 1 - start_pos]
                content = "\t".join(content)

                content = content[content.find("\n\n")+2:]
                director = content[:content.find("\t")]
                rating["director"] = parse_name(director)
        return ratings


class Actors:
    @staticmethod
    def get(ratings, exclude_formats="VG"):
        exclude_formats = exclude_formats.split(",")

        for listing in ["actors", "actresses"]:
            file_tmp = "/tmp/findex_%s.tmp" % listing
            if os.path.isfile(file_tmp):
                os.remove(file_tmp)

            print("Preparing %s. Estimated: 30 sec" % listing)

            chunk = 0
            f = open(file_tmp, "a", encoding=IMDB_ENCODING)
            buffer = ["\t"]
            buffer_max = 20000

            while True:
                data = read_data_file_chunks(listing, chunk=chunk)
                if not data:
                    break
                if chunk == 0:
                    data = data[data.index("THE %s LIST" % listing.upper()):][5:]

                for line in data:
                    if not line:
                        continue

                    if not line.startswith("\t"):
                        spl = [z for z in line.split("\t") if z]
                        if len(spl) != 2:
                            continue

                        _actor = "%s\t" % spl[0]
                        _line = Actors.validate_line(spl[1])

                        if "\t" in buffer[-1]:
                            buffer.pop()

                        if len(buffer) > buffer_max:
                            for b in buffer:
                                f.write(b + "\n")
                            buffer = []

                        buffer.append(_actor)
                        if _line:
                            buffer.append(_line)
                    else:
                        _line = Actors.validate_line(line)
                        if _line:
                            buffer.append(_line.strip())
                chunk += 1

            for b in buffer:
                f.write(b + "\n")
            f.close()

            actors = read_data_file(filepath=file_tmp)

            def find_in_actors(_title, _year, _actors):
                """returns actor name"""
                _needle = "%s (%d" % (_title, _year)

                rtn = []
                for i, _actor in enumerate(_actors):
                    if _actor.startswith(_needle):
                        w = copy.deepcopy(i)
                        while "\t" not in _actors[w]:
                            w -= 1

                        actor_line = _actors[w]
                        _actor = parse_name(actor_line)
                        if _actor not in rtn:
                            rtn.append(_actor)

                            if len(rtn) == 3:
                                break
                return rtn

            print("Parsing %s. Estimated: 1-2 min" % listing)
            for rating in ratings.ratings:
                title = rating["title"]
                year = rating["year"]

                actors_found = find_in_actors(title, year, actors)
                if actors_found:
                    if "actors" not in rating:
                        rating["actors"] = actors_found
                    else:
                        rating["actors"] = rating["actors"] + actors_found
            try:
                os.remove(file_tmp)
            except:
                pass
        return ratings

    @staticmethod
    def validate_line(inp):
        if not inp.endswith(">"):
            return
        if "{" in inp or "(V)" in inp or "(TV)" in inp:
            return
        if not re.search(r"<[1-3]>", inp):
            return
        return inp


class Plot:
    @staticmethod
    def get(ratings):
        plots = read_data_file("plot", "PLOT SUMMARIES LIST")
        plots = "\n".join([z.replace("\"", "") for z in plots[2:] if z])
        plots = [z.split("\n", 1) for z in \
                 plots.split("-------------------------------------------------------------------------------\n") if z]

        print("Parsing plots. Estimated: 20 sec")
        for rating in ratings.ratings:
            rating["plot"] = ""
            look = "MV: %s (%d)" % (rating["title"], rating["year"])

            for plot in plots:
                if not plot[0].startswith(look):
                    continue
                _plot = plot[1].replace("PL: ", " ").replace("\n", "")
                rating["plot"] = _plot.strip().replace("\t", " ")

        return ratings


def ps_exe(cmd, do_print=True):
    cmd = """/usr/bin/psql -t -h "%s" -p%d -U "%s" -d "%s" -c "%s" """ % (
        settings.db_hosts[0], settings.db_port, settings.db_user, settings.db_name, cmd)
    if do_print: print("Executing SQL: %s" % cmd)
    env = os.environ.copy()
    env["PGPASSWORD"] = settings.db_pass
    output = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, shell=True)
    rtn = output.stdout.read()
    return rtn


def ps_parse(results, columns):
    rtn = []
    results = results.decode("utf-8").split("\n")
    for r in [z for z in results if z]:
        spl = r.split("|", columns - 1)
        spl = [z.strip() for z in spl]

        spl[0] = int(spl[0])
        rtn.append(spl)
    return rtn


def update(tmp_folder="/tmp/", download_files=True, relink_files=True):
    """command injection through tmp_folder"""
    global TMP_FOLDER
    if not tmp_folder.endswith("/"):
        tmp_folder += "/"
    TMP_FOLDER = tmp_folder

    if download_files:
        for name in ["actors.list", "actresses.list", "directors.list", "genres.list", "plot.list", "ratings.list"]:
            # requests not available in pypy3 by default ;((
            # try:
            #     r = requests.get(url, stream=True)
            #     r.raise_for_status()
            # except Exception as ex:
            #     print("Exception: %s" % str(ex))
            #     sys.exit()
            #
            # fn = "%s%s.gz" % (tmp_folder, name)
            # with open(fn, 'wb') as f:
            #     for chunk in r.iter_content(1024 * 1024 * 4):
            #         f.write(chunk)

            url = "ftp://ftp.fu-berlin.de/pub/misc/movies/database/%s.gz" % name
            print("Fetching: %s" % url)
            fn = "%s%s.gz" % (tmp_folder, name)
            if os.path.isfile("%s%s.gz" % (tmp_folder, name)):
                try: os.remove("%s%s.gz" % (tmp_folder, name))
                except: pass
            if os.path.isfile("%s%s" % (tmp_folder, name)):
                try: os.remove("%s%s" % (tmp_folder, name))
                except: pass

            os.popen("wget %s -O %s" % (url, fn)).read()
            print("Done. Unpacking...")

            f = gzip.open(fn, 'rb')
            file_content = f.read()
            f.close()
            print("Unpacked.")

            f = open("%s%s" % (tmp_folder, name), "w")
            f.write(file_content)
            f.close()
            print("Saved as %s%s" % (tmp_folder, name))

    ratings = Ratings.get(min_votes=10000,
                          min_year=1960,
                          debug_max_lines=9000,
                          exclude_formats="VG,TV,V",
                          include_genres=True)
    ratings = Plot.get(ratings=ratings)
    ratings = Directors.get(ratings=ratings)
    ratings = Actors.get(ratings=ratings)
    print("Done parsing.")

    tosql = ToSql(ratings)
    copy_from = tosql()

    print("Updating postgres.")
    a1 = ps_exe("DELETE FROM meta_imdb_actors; DELETE FROM meta_imdb_directors; DELETE FROM meta_imdb;")
    print(a1)
    b1 = ps_exe("COPY meta_imdb FROM \'%s\'; REINDEX TABLE meta_imdb;" % copy_from["ratings"])
    print(b1)
    b2 = ps_exe("COPY meta_imdb_actors FROM \'%s\'; REINDEX TABLE meta_imdb_actors;" % copy_from["actors"])
    print(b2)
    b3 = ps_exe("COPY meta_imdb_directors FROM \'%s\'; REINDEX TABLE meta_imdb_directors;" % copy_from["directors"])
    print(b3)
    print("Cleanup files from tmp folder.")

    try:
        os.remove(copy_from["ratings"])
        os.remove(copy_from["actors"])
        os.remove(copy_from["directors"])
    except:
        pass

    if relink_files:
        relink()


def relink():
    print("Syncing/Linking old file entries in DB.")
    updates = ""

    meta_imdb = ps_exe("SELECT id,title,year FROM meta_imdb;")
    meta_imdb = ps_parse(meta_imdb, columns=3)

    files = ps_exe("SELECT id,meta_info FROM files WHERE meta_info->>'ptn' != 'null' and file_size > 134217728;")
    files = ps_parse(files, columns=2)
    for f in files:
        blob = json.loads(f[1])
        year = blob["ptn"].get("year")
        title = blob["ptn"].get("title")
        if not year or not title:
            continue
        for meta in meta_imdb:
            if meta[1] == title and int(meta[2]) == year:
                updates += """UPDATE files SET meta_imdb_id=%d;""" % meta[0]
    if updates:
        ps_exe(cmd=updates, do_print=False)
        print("Done.")


if not hasattr(sys, "pypy_translation_info"):
    raise Exception("requires pypy3 to run, not cPython")

update(download_files=True, relink_files=True)
