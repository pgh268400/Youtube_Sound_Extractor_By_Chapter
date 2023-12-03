import glob
import json
import os
from pprint import pprint
import shutil
import sys
import yt_dlp
from module.module import add_album_art, convert_base_to_ranged_chapter, filename_remover, make_base_chapter, run_ffmpeg
from yt_dlp import YoutubeDL
from type.type import RangedChapter


# run_mp4art(['--add', 'thumbnails\\0.png', "output\\L L L .m4a"])
r"""
    정규식 1번
    (.+?)[ ]+(?:│|[|])*[ ]*(\d+:\d+:\d+|\d+:\d+)
    01. Durarara!! OP2 │ 0:00
    02. Assassination classroom S2 OP2 │ 4:44
    03. Hunter x Hunter (2011) OP │ 8:51
    04. Noragami Aragoto OP │ 13:01
    05. Fate/Stay Night Unlimited Blade Works  OP2 │ 17:08
    => output : title : 01. Durarara!! OP2 , time : 0:00

    정규식 2번 (순서 변경)
    (\d+:\d+:\d+|\d+:\d+)[ ]+(?:│|[|])*[ ]*(.+)
    00:00 유우리 - 여름소리
    03:58 녹황색사회 - 리트머스
    08:09 요네즈 켄시 - 말과 사슴
    12:36 후지이 카제 - 상냥함
    16:39 게스노키와미오토메 - 킬러볼
    => output : title : 유우리 - 여름소리 , time : 00:00
"""

# 유튜브 영상 주소 입력
url = input("유튜브 영상 주소를 입력해주세요 : ")
print("유튜브 영상 정보를 가져오는 중...")

# yt-dlp로 영상 정보 가져오기
ydl = YoutubeDL({"quiet": True})
info = ydl.extract_info(url, download=False)
ydl.close()  # with 을 쓰지 않아서 직접 close 해줘야함
if not info:
    print("유튜브 영상 정보를 가져오는데 실패했습니다.")
    exit()

# info 데이터 파일에 저장
with open('info.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=0)

title: str = info['title']
duration: str = info['duration_string']
chapters = info['chapters']
print("제목 :", title)
print("영상 길이 :", duration)

if (chapters != None):
    # 영상에 이미 챕터가 존재하는 경우 RangedChapter 에 맞게 변환한다.
    print("영상에 이미 챕터가 존재합니다, 작업을 위해 알맞게 변환합니다.")

    ranged_chapter = []
    for i, chapter in enumerate(chapters):
        ranged_chapter.append(
            RangedChapter(
                # filename_remover 작업
                title=filename_remover(chapter['title']), start_time=chapter['start_time'], end_time=chapter['end_time']
            ))
    # 변환 후 원래 챕터에 반영
    chapters = ranged_chapter

else:
    print('챕터를 입력해주세요. 다 입력했으면 Ctrl + Z (Ctrl + D) 를 입력합니다. :')

    contents: list[str] = sys.stdin.readlines()
    contents_join: str = ''.join(contents)

    print("챕터 생성 진행 중...")
    base_chapter = make_base_chapter(contents_join)
    pprint(base_chapter)

    print('챕터 변환을 수행합니다.')
    ranged_chapter = convert_base_to_ranged_chapter(base_chapter, duration)
    chapters = ranged_chapter

# 여기까지 오면 chapters는 확정된 상태 = Not Empty
print(chapters)

# filename_remover 작업
title = filename_remover(title)


# 최고 화질 + 최고 음질로 영상 다운로드
# 참고 : https://github.com/yt-dlp/yt-dlp/issues/3398\
# mp4 영상은 최고 용량이 webm 용량 대비 너무 커서 webm을 택했으나
# mp4는 음원 분리가 바로 되나 webm은 재 인코딩 과정이 필요해 매우 오래 걸림.
# 따라서 어쩔 수 없이 mp4를 택함.

ext = 'mp4'  # 수정 금지!
thumbnail_folder = 'thumbnails'  # 썸네일 폴더명
output_folder = 'output'  # 최종 결과물 폴더명
print('최고 품질로 영상을 다운로드 합니다.')

with yt_dlp.YoutubeDL({'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'merge_output_format': ext, 'outtmpl': {'default': '%(title)s.%(ext)s'}}) as ydl:
    ydl.download([url])
print('다운로드가 완료되었습니다.')

# 각 챕터 시작 시간의 썸네일을 ffmpeg를 이용해 추출한다.
print('썸네일을 추출합니다.')

# 썸네일 저장용 폴더 생성
os.makedirs(thumbnail_folder, exist_ok=True)

# 썸네일 추출시 +- 전체적으로 몇 초 보정할 지 오프셋값
total_offset = 3  # 이곳을 수정

# 이 곳 아래 변수를 조정해 특정 순번의 썸네일에만 오프셋을 따로 줄 수도 있음
custom_offset = {
    1: 4,  # 1번 챕터에만 +N초 오프셋을 줌 (total_offset과 합산됨)
    # 2: -5,
    # 3: -8,
    # 4: 7,
}

# ffmpeg로 챕터 시작 시간의 썸네일 추출
for i, chapter in enumerate(chapters):
    copy_offset = total_offset
    # custom offset이 적용된 경우 해당 순번의 썸네일에만 오프셋을 따로 줌 (total_offset과 합산됨)
    if i+1 in custom_offset:
        copy_offset = total_offset + custom_offset[i+1]

    # 썸네일 추출
    time = str(int(chapter.start_time) + copy_offset)
    output = run_ffmpeg(  # -y 옵션 : 덮어쓰기
        ['-y', '-ss', time, '-i', f'{title}.{ext}', '-vframes', '1', os.path.join(thumbnail_folder, f"{i}.png")])
    print(output)
print('썸네일 추출이 완료되었습니다.')

# 다운로드 받은 영상에서 무손실 음원 m4a를 추출한다
print('음원을 추출합니다.')
output = run_ffmpeg(
    ['-y', '-i', f'{title}.{ext}', '-vn', '-acodec', 'copy', f'{title}.m4a'])

# 추출한 음원을 챕터별로 자른다.
print('음원을 챕터별로 자릅니다.')
os.makedirs(output_folder, exist_ok=True)
for i, chapter in enumerate(chapters):
    # 챕터별 음원 추출
    output = run_ffmpeg(
        ['-y', '-i', f'{title}.m4a', '-ss', str(int(chapter.start_time)), '-to', str(int(chapter.end_time)), '-c', 'copy', os.path.join(output_folder, f'{chapter.title}.m4a')])
    print(f'{chapter.title}.m4a 추출 완료')

# 챕터별로 자른 음원에 썸네일을 붙인다.
print('썸네일을 적용합니다.')

# 썸네일 폴더의 모든 파일을 가져온다.
# thumbnail_files = os.listdir(thumbnail_folder)
thumbnail_files = glob.glob(os.path.join(thumbnail_folder, '*.png'))

for i, thubnail_file in enumerate(thumbnail_files):
    # 썸네일 적용
    # output = run_mp4art(
    #     ["--add", file, os.path.join(output_folder, chapters[i].title + ".m4a")])

    m4a_path = os.path.join(output_folder, chapters[i].title + ".m4a")

    add_album_art(m4a_path, thubnail_file)

    print(f'{chapters[i].title}.m4a 썸네일 적용 완료')

# 작업 완료 후 다운로드 받은 영상, 추출한 음원, 썸네일 폴더를 삭제한다.
os.remove(f'{title}.{ext}')
os.remove(f'{title}.m4a')
shutil.rmtree(thumbnail_folder)

print("작업이 완료되었습니다.")
