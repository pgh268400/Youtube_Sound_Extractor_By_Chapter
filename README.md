# Youtube_Sound_Extractor_By_Chapter

유튜브의 통짜로 합쳐진 노래 영상 파일들을 챕터별로 분리해서 저장하는 프로그램입니다.

## LOGIC

1. 유튜브 노래 영상 파일을 다운로드 받습니다.
2. 영상 파일에서 m4a 또는 mp3 파일을 추출합니다.
3. 챕터 별로 추출한 음원 파일을 잘라서 각각 저장합니다.
4. 챕터 별로 썸네일을 추출합니다.
5. 각각 저장된 음원 파일에 썸네일을 붙입니다.

## Dependency

해당 프로그램을 사용하기 위해선 `yt-dlp`, `ffmpeg` 설치가 필요합니다. 리눅스의 경우 apt-get, 윈도우의 경우 choco나 기타 환경 변수 설정을 통해 설치해주세요.
