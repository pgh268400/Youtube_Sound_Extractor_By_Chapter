from datetime import datetime, timedelta
import re
import subprocess
import requests
from type.type import BaseChapter, RangedChapter

# 프로세스 실행하고 결과를 반환하는 함수


def run_process(command: list[str]) -> str:
    # command ex) ['ls', '-al']

    # 명령어 실행 후, 결과를 output에 저장
    # text = True : output을 text로 저장,
    # encoding은 기본이 cp949라 문제 없이 저장할려면 utf-8로 설정
    try:
        output: str = subprocess.check_output(
            command, stderr=subprocess.STDOUT, encoding='utf-8', text=True)
    except:
        raise Exception('명령어 실행에 실패했습니다.')

    return output

# ffmpeg 실행하고 결과를 반환하는 함수 (일종의 run_process의 wrapper 함수)


def run_ffmpeg(command: list[str]) -> str:
    output = run_process(["ffmpeg", *command])
    return output


def get_title_from_youtube(url) -> str:
    res = requests.get(url)
    title = re.search('(?<=<title>).+?(?=</title>)',
                      res.text, re.DOTALL)
    if title:
        title = title.group().replace(' - YouTube', '')
    else:
        raise Exception('Title not found')
    return title

# 1:30:00, 30:00, 30 와 같은 시간 형식을 초로 변환
# 1:30:00 => 5400.0
# 30:00 => 1800.0
# 30 => 30.0


def convert_to_seconds(formatted_time: str) -> float:
    # 시간 형식에 따라 적절한 포맷을 선택
    formats = ['%H:%M:%S', '%M:%S', '%S']

    for fmt in formats:
        try:
            # 주어진 형식으로 시간을 파싱
            time_obj = datetime.strptime(formatted_time, fmt)

            # timedelta를 사용하여 초로 변환
            seconds = timedelta(
                hours=time_obj.hour,
                minutes=time_obj.minute,
                seconds=time_obj.second
            ).total_seconds()
            return seconds
        except ValueError:
            pass

    # 올바른 형식이 없는 경우 예외 처리
    raise ValueError("올바른 시간 형식이 아닙니다.")

# 유저가 입력한 챕터 형식을 파싱해 BaseChapter 객체로 반환


def make_base_chapter(user_input: str) -> list[BaseChapter]:
    pattern_lst = [
        # 01. Durarara!! OP2 │ 0:00
        r'(.+?)[ ]+(?:│|[|])*[ ]*(\d+:\d+:\d+|\d+:\d+)',
        r'(\d+:\d+:\d+|\d+:\d+)[ ]+(?:│|[|])*[ ]*(.+)'  # 00:00 유우리 - 여름소리
    ]

    success_chapter = False  # 챕터를 정상적으로 파싱했는지 여부
    raw_parsed_chapter = []

    pattern_idx = 0
    for i, pattern in enumerate(pattern_lst):
        pattern_idx = i
        raw_parsed_chapter: list[tuple[str, str]] = re.findall(
            pattern, user_input)

        if raw_parsed_chapter:
            # print('챕터가 정상적으로 파싱되었습니다.')
            success_chapter = True
            break

    if not success_chapter:
        raise Exception('챕터 파싱에 실패했습니다. 챕터 형식을 확인해주세요.')

    parsed_chapter: list[BaseChapter] = []
    # 첫번째 패턴 : 숫자가 뒤에 오는 경우
    print(pattern_idx)
    if pattern_idx == 0:
        parsed_chapter = [BaseChapter(title, time)
                          for title, time in raw_parsed_chapter]
    # 두번째 패턴 : 숫자가 앞에 오는 경우
    elif pattern_idx == 1:
        parsed_chapter = [BaseChapter(title, time)
                          for time, title in raw_parsed_chapter]

    return parsed_chapter

# 베이스 챕터들을 레인지 챕터로 변환해주는 함수.
# BaseChapter 리스트 객체를 RangedChapter 리스트 객체로 변환한다.
# 이 함수는 BaseChapter 리스트와 영상의 길이를 인자로 받는다.
# 영상의 길이 ex) 1:30:00, 30:00, 30


def convert_base_to_ranged_chapter(base_chapter: list[BaseChapter], video_duration: str) -> list[RangedChapter]:
    ranged_chapter: list[RangedChapter] = []
    for i, element in enumerate(base_chapter):
        # 마지막 챕터인 경우 끝은 영상 끝까지
        if i == len(base_chapter) - 1:
            ranged_chapter.append(
                RangedChapter(
                    title=element.title,
                    start_time=convert_to_seconds(element.timeline),
                    end_time=convert_to_seconds(video_duration)
                )
            )
            break
        ranged_chapter.append(
            RangedChapter(
                title=element.title,
                start_time=convert_to_seconds(element.timeline),
                end_time=convert_to_seconds(
                    base_chapter[i+1].timeline)  # 다음 챕터의 시작 시간
            )
        )
    return ranged_chapter


if __name__ == "__main__":
    print(convert_to_seconds('1:30:00'))
    print(convert_to_seconds('30:00'))
    print(convert_to_seconds('30'))
