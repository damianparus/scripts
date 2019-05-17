import click
import glob


@click.command()
@click.option('--source', '-s', required=True)
@click.option('--target', '-t', required=True)
def main(source, target):
    for file in glob.glob(source+"/*"):
        command = 'exiftool {}'.format(file)
        print(command)

main()
