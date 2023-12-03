# Allow direct execution
import yt_dlp.options
import yt_dlp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


create_parser = yt_dlp.options.create_parser


def parse_patched_options(opts):
    patched_parser = create_parser()
    patched_parser.defaults.update({
        'ignoreerrors': False,
        'retries': 0,
        'fragment_retries': 0,
        'extract_flat': False,
        'concat_playlist': 'never',
    })
    yt_dlp.options.create_parser = lambda: patched_parser
    try:
        return yt_dlp.parse_options(opts)
    finally:
        yt_dlp.options.create_parser = create_parser


default_opts = parse_patched_options([]).ydl_opts


def cli_to_api(opts, cli_defaults=False):
    opts = (yt_dlp.parse_options if cli_defaults else parse_patched_options)(
        opts).ydl_opts

    diff = {k: v for k, v in opts.items() if default_opts[k] != v}
    if 'postprocessors' in diff:
        diff['postprocessors'] = [pp for pp in diff['postprocessors']
                                  if pp not in default_opts['postprocessors']]
    return diff


# 원래 사용한대로 인자를 넘겨주면 yt-dlp class 에서 사용하는 인자로 변환해준다.
# 여기서 인자가 어떻게 변하는지 파악하고 사용하면 된다.
if __name__ == '__main__':
    from pprint import pprint

    print('\n전달된 인수는 다음으로 변환됩니다:\n')
    pprint(cli_to_api(sys.argv[1:]))
    print('\n이를 CLI 기본값과 결합하면 다음으로 표현됩니다:\n')
    pprint(cli_to_api(sys.argv[1:], True))
