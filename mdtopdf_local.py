import glob
import os
def main():
    files = glob.glob('./*.md')
    with open('tmp.md', 'w+') as f:
        for i in files:
            f.write(open(i).read())
    os.system('md2pdf tmp.md test.pdf')  # 需要安装md2pdf
    os.remove('tmp.md')
    print('finished!')
if __name__ == '__main__':
    main()