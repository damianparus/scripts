# Examples:
# python3 ./manage_media.py --source '/backup/camera/*.MTS' --target /backup/x --do-it
# python3 /home/halley/scripts/manage_media.py --source './*' --target /backup/media --do-it
import click
import glob
import subprocess
import re
import os
from datetime import datetime

def convert_line_to_datetime(line):
    clean_string = ':'.join(line.split(':')[1:]).strip()
    clean_string = clean_string.replace('DST', '').strip()
    if clean_string.find('+') != -1:
        clean_string = re.sub(r'(\+\d\d):(\d\d)', r'\1\2', clean_string)
        converted_date = datetime.strptime(clean_string, '%Y:%m:%d %H:%M:%S%z')
    elif clean_string.find('.') != -1:
       converted_date = datetime.strptime(clean_string, '%Y:%m:%d %H:%M:%S.%f')
    else:
       converted_date = datetime.strptime(clean_string, '%Y:%m:%d %H:%M:%S')
    return converted_date

def get_create_datetime(exif_output):
    headers = ['Date/Time Original', 'Media Create Date', 'File Modification Date/Time']
    lines = exif_output.split('\n')
    dates = {}
    for line in lines:
        for header in headers:
            if line.startswith(header):
                dates[header] = convert_line_to_datetime(line)
    for header in headers:
        if header in dates:
            return dates[header]

    raise Exception('\n'.join(lines))

@click.command()
@click.option('--source', '-s', required=True)
@click.option('--target', '-t', required=True)
@click.option('--do-it', is_flag=True)
def main(source, target, do_it):
    for current_file in glob.glob(source):
        proc = subprocess.Popen(['exiftool', current_file], stdout=subprocess.PIPE)
        out = proc.communicate()[0]
        if proc.returncode != 0:
            print('Error: {}'.format(current_file))
            continue
        create_datetime = get_create_datetime(out.decode("utf-8", errors='ignore'))
        create_datetime_string = create_datetime.strftime('%Y/%m-%d')

        target_dir = '{}/{}'.format(target, create_datetime_string)
        current_file_target_full_path = '{}/{}'.format(target_dir, os.path.basename(current_file))
        current_file_target_exists = os.path.isfile(current_file_target_full_path)
        if current_file_target_exists:
            print('File exists: {file}, date: {date}, {current_file_target_full_path}'.format(file=current_file, date=create_datetime_string, current_file_target_full_path=current_file_target_full_path))
            if do_it:
                subprocess.run(['mv', '-b', current_file, '/tmp'])
        else:
            if do_it:
                subprocess.run(['mkdir', '-p', target_dir])
                subprocess.run([
                    'mv',
                    '-n',
                    current_file,
                    target_dir
                ])
            print('Done: {file}, date: {date}'.format(file=current_file, date=create_datetime_string))

main()
