import re
import time
import subprocess

import requests

# 프로세스 실행하고 결과값을 반환하는 함수 (화면 출력은 하지 않는다.)


def run_process(command: list[str]) -> str:
    try:
        # command ex) ['ls', '-al']
        output: str = subprocess.check_output(
            command, stderr=subprocess.STDOUT, encoding='utf-8', text=True)
        return output.rstrip('\n')
    except:
        raise Exception('프로세스 실행에 실패했습니다.')


# 유튜브 다운로드 함수


def download_video(url: str, option: list[str] = []) -> str:
    # 유튜브 다운로드 명령어
    # *options: 리스트를 풀어서 넣어줌
    # * : unpacking
    command: list[str] = ['yt-dlp', url, *option]

    # 유튜브 다운로드 실행
    output: str = run_process(command)
    return output


# 시간 측정
start = time.time()

# yt-dlp --download-sections "*1-2" "https://www.youtube.com/watch?v=9Y3eu5Q-xP0&t=2070s"
# 특정지점 다운로드
url = 'https://www.youtube.com/watch?v=9Y3eu5Q-xP0&t=2070s'
option = ['--print', 'title']
title = download_video(url, option)
print(title)

end = time.time()
print(f'실행 시간 1 : {end - start}')

start = time.time()

res = requests.get(url)
title = re.search('(?<=<title>).+?(?=</title>)',
                  res.text, re.DOTALL).group().strip()
print(title)

end = time.time()
print(f'실행 시간 2 : {end - start}')


option = ['--download-sections', '*1-2']
output = download_video(url, option)
print(output)
