docker build zomboPG/ -t zombopg:0.1 --label zomboPG:0.1
docker build zomboES -t zomboes:0.1 --label zomboES:0.1
mkdir -p findex/findex/
cp -r ../findex_gui/* findex/findex/
docker build findex -t findexgui --label findexgui:0.1
