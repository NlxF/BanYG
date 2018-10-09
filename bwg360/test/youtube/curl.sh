#!/bin/bash

echo "start curling"
curl -X GET -s "127.0.0.1:5001/download?url=http://v.youku.com/v_show/id_XMzAyMzk2NzkxNg==.html?spm=a2hww.20023042.m_226600.5~5!2~5~5~5~5~A&f=49716696" -o "file1.mp4" && echo "done1" &
curl -X GET -s "127.0.0.1:5001/download?url=http://v.youku.com/v_show/id_XMzAyMzk2NzkxNg==.html?spm=a2hww.20023042.m_226600.5~5!2~5~5~5~5~A&f=49716696" -o "file2.mp4" && echo "done2" &
curl -X GET -s "127.0.0.1:5001/download?url=http://v.youku.com/v_show/id_XMzAyMzk2NzkxNg==.html?spm=a2hww.20023042.m_226600.5~5!2~5~5~5~5~A&f=49716696" -o "file3.mp4" && echo "done3" &
curl -X GET -s "127.0.0.1:5001/download?url=http://v.youku.com/v_show/id_XMzAyMzk2NzkxNg==.html?spm=a2hww.20023042.m_226600.5~5!2~5~5~5~5~A&f=49716696" -o "file4.mp4" && echo "done4" &
echo "waiting..."
wait