#!/usr/bin/env python
# coding: utf-8

# 版本
from core.Utils import EDITION

from core.Exceptions import ArgumentError
from core.Exceptions import MainPrint
# 包导入
import sys
import os
# 文件路径
from core.Medias import MediaObj
from core.FilePaths import Filepath
# 配置
from core.ProjConfig import Config
from core.ScriptParser import RplGenLog,MediaDef,CharTable,Script
# 输出
from core.OutputType import PreviewDisplay,ExportVideo,ExportXML

# 主程序
class ReplayGenerator:
    # 初始化参数
    def __init__(self,args):
        try:
            # 外部输入文件
            self.log_path = args.LogFile
            self.media_path = args.MediaObjDefine
            self.char_path = args.CharacterTable
            self.output_path = args.OutputPath
            self.json_path = args.Json
            # 输出方式
            self.export_video = args.ExportVideo
            self.export_xml = args.ExportXML
            # 配置
            if self.json_path != None:
                # 如果是工程文件（.rgpj）输入
                input_json = Script(json_input=self.json_path)
                # 工程文件所在目录，同时是 @ 相对路径的基准目录
                project_dir = Filepath(self.json_path).directory()
                Filepath.set_media_path(project_dir)
                self.config = Config(dict_input=input_json.struct['config'])
                self.config.execute()
                # 读取输入工程结构
                self.medef = MediaDef(dict_input=input_json.struct['mediadef'])
                self.chartab = CharTable(dict_input=input_json.struct['chartab'])
                # 一份工程可以包含多份剧本：--LogFile 传入剧本名则用它，否则取第一份
                logfile_struct:dict = input_json.struct['logfile']
                if (self.log_path is not None) and (self.log_path in logfile_struct):
                    log_key = self.log_path
                else:
                    log_key = next(iter(logfile_struct))
                print(MainPrint('LoadRGL'), f'[{log_key}]')
                self.rplgenlog = RplGenLog(dict_input=logfile_struct[log_key])
                # 没有指定输出目录时，缺省放在工程目录下
                if self.output_path is None:
                    self.output_path = project_dir + 'output/'
                if os.path.isdir(self.output_path) == False:
                    os.makedirs(self.output_path)
            else:
                # 通过args输入
                self.config = Config(argparse_input=args)
                self.config.execute()
                # 检查输入文件可用性
                for path in [self.log_path,self.media_path,self.char_path]:
                    if path is None:
                        raise ArgumentError('MissInput')
                    if os.path.isfile(path) == False:
                        raise ArgumentError('FileNotFound',path)
                    self.medef = MediaDef(file_input=self.media_path)
                    self.chartab = CharTable(file_input=self.char_path)
                    self.rplgenlog = RplGenLog(file_input=self.log_path)
        # debug
        except ArgumentError as E:
            self.medef = MediaDef(file_input='./toy/MediaObject.txt')
            self.chartab = CharTable(file_input='./toy/CharactorTable.tsv')
            self.rplgenlog = RplGenLog(file_input='./toy/LogFile.rgl')
            self.output_path = './test_output'
        except Exception as E:
            print(E)
            sys.exit(1)
        self.main()
   # 执行输入文件
    def execute_input(self):
        # TODO：把这个对类对象的操作，想个办法封装起来
        MediaObj.export_xml = False
        MediaObj.output_path = self.output_path
        # log
        try:
            # 初始化媒体
            self.medef.execute()
            # 初始化角色表
            self.chartab.execute()
            # 初始化log文件
            self.rplgenlog.execute(media_define=self.medef,char_table=self.chartab,config=self.config)
        except Exception as E:
            print(E)
            sys.exit(1)
    # 主流程
    def main(self):
        # welcome
        print(MainPrint('Welcome',EDITION))
        # 输出目录：缺省路径，并统一为带结尾 '/' 的写法（输出文件名是直接拼在目录后面的）
        if self.output_path is None:
            self.output_path = './test_output/'
        self.output_path = Filepath.normalize_dir(self.output_path)
        # 执行输入
        self.execute_input()
        # 输出方式：导出MP4 / 导出PR项目 / 预览播放
        if self.export_video:
            print(MainPrint('ExportMp4'))
            if os.path.isdir(self.output_path) == False:
                os.makedirs(self.output_path)
            flag = ExportVideo(
                rplgenlog   = self.rplgenlog,
                config      = self.config,
                output_path = self.output_path,
                key         = None
                ).main()
        elif self.export_xml:
            print(MainPrint('ExportXML'))
            if os.path.isdir(self.output_path) == False:
                os.makedirs(self.output_path)
            flag = ExportXML(
                rplgenlog   = self.rplgenlog,
                config      = self.config,
                output_path = self.output_path,
                key         = None
                ).main()
        else:
            flag = PreviewDisplay(
                rplgenlog   = self.rplgenlog,
                config      = self.config
                ).main()
        # 退出状态
        print(MainPrint('Error' if flag != 0 else ('Video' if self.export_video else 'End')))
        return flag

if __name__ == '__main__':
    import argparse
    # 外部参数输入
    # 参数处理
    ap = argparse.ArgumentParser(description="Generating your TRPG replay video from logfile.")
    ap.add_argument("-l", "--LogFile", help='The standerd input of this programme, which is mainly composed of TRPG log.',type=str)
    ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
    ap.add_argument("-t", "--CharacterTable", help='The correspondence between character and media elements, using tab separated text file or Excel table.',type=str)
    ap.add_argument("-j", "--Json", help='Use the config from json file, instead of arguments from command.',type=str)
    ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the project timeline and breakpoint file.',type=str,default=None)
    # 选项
    ap.add_argument("-F", "--FramePerSecond", help='Set the FPS of display, default is 30 fps, larger than this may cause lag.',type=int,default=30)
    ap.add_argument("-W", "--Width", help='Set the resolution of display, default is 1920, larger than this may cause lag.',type=int,default=1920)
    ap.add_argument("-H", "--Height", help='Set the resolution of display, default is 1080, larger than this may cause lag.',type=int,default=1080)
    ap.add_argument("-Z", "--Zorder", help='Set the display order of layers, not recommended to change the values unless necessary!',type=str,
                    default='BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS')
    # 用于语音合成的key
    ap.add_argument("-K", "--AccessKey", help='Your AccessKey, to use with --SynthsisAnyway',type=str,default="Your_AccessKey")
    ap.add_argument("-S", "--AccessKeySecret", help='Your AccessKeySecret, to use with --SynthsisAnyway',type=str,default="Your_AccessKey_Secret")
    ap.add_argument("-A", "--Appkey", help='Your Appkey, to use with --SynthsisAnyway',type=str,default="Your_Appkey")
    ap.add_argument("-U", "--Azurekey", help='Your Azure TTS key.',type=str,default="Your_Azurekey")
    ap.add_argument("-R", "--ServRegion", help='Service region of Azure.', type=str, default="eastasia")

    # 用于导出视频的质量值
    ap.add_argument("-Q", "--Quality", help='Choose the quality (ffmpeg crf) of output video, to use with --ExportVideo.',type=int,default=24)
    # Flags
    ap.add_argument('--ExportXML',help='Export a xml file to load in Premiere Pro, some .png file will be created at same time.',action='store_true')
    ap.add_argument('--ExportVideo',help='Export MP4 video file, this will disables interface display',action='store_true')
    ap.add_argument('--SynthesisAnyway',help='Execute speech_synthezier first, and process all unprocessed asterisk time label.',action='store_true')
    ap.add_argument('--FixScreenZoom',help='Windows system only, use this flag to fix incorrect windows zoom.',action='store_true')
    ap.add_argument("--ForceSplitClip", help='Force to separate clips at breakpoints while exporting PR sequence.',action='store_true' )
    # 语言
    ap.add_argument("--Language",help='Choose the language of running log',default='en',type=str)
    # 主
    args = ap.parse_args()
    try:
        ReplayGenerator(args=args)
    except:
        from traceback import print_exc
        print_exc()