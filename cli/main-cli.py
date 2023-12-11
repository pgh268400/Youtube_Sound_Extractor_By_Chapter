import glob
import json
import os
from pprint import pprint
import shutil
import sys
import yt_dlp
from module.config import Config
from module.module import (
    add_album_art,
    convert_base_to_ranged_chapter,
    filename_remover,
    get_youtube_info,
    make_base_chapter,
    run_ffmpeg,
)
from natsort import natsorted
from type.type import RangedChapter

# 설정 파일에서 설정값을 가져온다.
settings_file_path = "./settings.json"
cfg = Config(settings_file_path)
thumbnail_folder = cfg.get().thumbnail_folder
output_folder = cfg.get().output_folder
total_offset = cfg.get().total_offset
custom_offset = cfg.get().custom_offset

# 유튜브 영상 주소 입력
url = input("유튜브 영상 주소를 입력해주세요 : ")
print("유튜브 영상 정보를 가져오는 중...")
info = get_youtube_info(url)

# info 데이터 파일에 저장
with open("info.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=0)

title: str = info["title"]
duration: str = info["duration_string"]
chapters = info["chapters"]
print("제목 :", title)
print("영상 길이 :", duration)


# 유저로부터 챕터를 입력받고 파싱
def parse_chapter_by_user() -> list[RangedChapter]:
    print("챕터를 입력해주세요. 다 입력했으면 Ctrl + Z (Ctrl + D) 를 입력합니다. :")

    contents: list[str] = sys.stdin.readlines()
    contents_join: str = "".join(contents)

    print("챕터 생성 진행 중...")
    base_chapter = make_base_chapter(contents_join)
    pprint(base_chapter)

    print("챕터 변환을 수행합니다.")
    ranged_chapter = convert_base_to_ranged_chapter(base_chapter, duration)
    return ranged_chapter


# yt-dlp에서 가져온 챕터 내역을 프로그램에 알맞게 변환
def parse_chapter_by_yt_dlp(chapters) -> list[RangedChapter]:
    ranged_chapter = []
    for i, chapter in enumerate(chapters):
        ranged_chapter.append(
            RangedChapter(
                # filename_remover 작업
                title=filename_remover(chapter["title"]),
                start_time=chapter["start_time"],
                end_time=chapter["end_time"],
            )
        )
    return ranged_chapter


if chapters != None:
    # 영상에 이미 챕터가 존재하는 경우 RangedChapter 에 맞게 변환한다.
    answer = input("영상에 이미 챕터가 존재합니다 영상의 챕터를 사용하시겠습니까 ? (y/n) : ")
    if answer.lower() == "y":
        chapters = parse_chapter_by_yt_dlp(chapters)
    else:
        chapters = parse_chapter_by_user()
else:
    chapters = parse_chapter_by_user()

# 여기까지 오면 chapters는 확정된 상태 = Not Empty
pprint(chapters)

# filename_remover 작업
title = filename_remover(title)

# 최고 화질 + 최고 음질로 영상 다운로드
# 참고 : https://github.com/yt-dlp/yt-dlp/issues/3398
# mp4 영상은 최고 용량이 webm 용량 대비 너무 커서 webm을 택했으나
# mp4는 음원 분리가 바로 되나 webm은 재 인코딩 과정이 필요해 매우 오래 걸림.
# 따라서 어쩔 수 없이 mp4를 택함.

ext = "mp4"  # 수정 금지!

print("최고 품질로 영상을 다운로드 합니다.")

with yt_dlp.YoutubeDL(
    {
        # 최고 품질 영상 mp4 & 최고 음질 m4a 로 받으나, 영상의 경우 FHD 이하로 제한한다.
        "format": f"bestvideo[height<=1080][ext={ext}]+bestaudio[ext=m4a]/best[ext={ext}]/best",
        "merge_output_format": ext,
        "outtmpl": {"default": "%(title)s.%(ext)s"},  # 제목.확장자 형식으로 저장
        "throttledratelimit": 102400,
        "concurrent_fragment_downloads": 10,  # 동시에 10개의 영상 조각을 다운로드
    }
) as ydl:
    ydl.download([url])
print("다운로드가 완료되었습니다.")

# 각 챕터 시작 시간의 썸네일을 ffmpeg를 이용해 추출한다.
print("썸네일을 추출합니다.")

# 썸네일 저장용 폴더 생성
os.makedirs(thumbnail_folder, exist_ok=True)

# ffmpeg로 챕터 시작 시간의 썸네일 추출
for i, chapter in enumerate(chapters):
    copy_offset = total_offset
    # custom offset이 적용된 경우 해당 순번의 썸네일에만 오프셋을 따로 줌 (total_offset과 합산됨)
    if i + 1 in custom_offset:
        copy_offset = total_offset + custom_offset[i + 1]
    # 썸네일 추출
    time = str(int(chapter.start_time) + copy_offset)
    output = run_ffmpeg(
        [
            # -y 옵션 : 덮어쓰기
            "-y",
            "-ss",
            time,
            "-i",
            f"{title}.{ext}",
            "-vframes",
            "1",
            os.path.join(thumbnail_folder, f"{i}.png"),
        ]
    )
    print(output)
print("썸네일 추출이 완료되었습니다.")

# 다운로드 받은 영상에서 무손실 음원 m4a를 추출한다
print("음원을 추출합니다.")
output = run_ffmpeg(
    ["-y", "-i", f"{title}.{ext}", "-vn", "-acodec", "copy", f"{title}.m4a"]
)

# 추출한 음원을 챕터별로 자른다.
print("음원을 챕터별로 자릅니다.")
os.makedirs(output_folder, exist_ok=True)
for i, chapter in enumerate(chapters):
    # 챕터별 음원 추출
    output = run_ffmpeg(
        [
            "-y",
            "-i",
            f"{title}.m4a",
            "-ss",
            str(int(chapter.start_time)),
            "-to",
            str(int(chapter.end_time)),
            "-c",
            "copy",
            os.path.join(output_folder, f"{chapter.title}.m4a"),
        ]
    )
    print(f"{chapter.title}.m4a 추출 완료")
# 챕터별로 자른 음원에 썸네일을 붙인다.
print("썸네일을 적용합니다.")

# 썸네일 폴더의 모든 파일을 가져온다.
# thumbnail_files = os.listdir(thumbnail_folder)
thumbnail_files = glob.glob(os.path.join(thumbnail_folder, "*.png"))
thumbnail_files = natsorted(thumbnail_files)

for i, chapter in enumerate(chapters):
    m4a_path = os.path.join(output_folder, chapter.title + ".m4a")
    add_album_art(m4a_path, thumbnail_files[i])
    print(f"{chapter.title}.m4a 썸네일 적용 완료")

# 작업 완료 후 다운로드 받은 영상, 추출한 음원, 썸네일 폴더를 삭제한다.
# os.remove(f"{title}.{ext}")
# os.remove(f"{title}.m4a")
# shutil.rmtree(thumbnail_folder)

print("작업이 완료되었습니다.")
