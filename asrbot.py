import speech_recognition as sr
import logging
from Audio_player import play_audio, play_wakeup, play_waiting
import os
from request import synthesize_speech
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class asrbot():
    awakeword="小邓"
    #状态有： 监听：DETECTING   对话：CHATING     
    status="DETECTING"
    def recognize_speech_from_mic(self,recognizer, microphone):
    # check that recognizer and microphone arguments are appropriate type
        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            response["transcription"] = recognizer.recognize_google(audio,language="zh-CN")
            print(response["transcription"])
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"
        return response
    def run(self):
        logger.info('running...')
        while True:
            #动态检测唤醒词
            if self.status=="DETECTING":
                if not self.run_detect_wakeup_word():
                    continue
            elif self.status=="CHATING":
                # 1. 唤醒提示音
                logger.info('wakeup & listening...')
                play_wakeup()

                # 2. 识别用户输入的语音
                play_audio('request_question.wav')
                recognizer = sr.Recognizer()
                microphone = sr.Microphone()
                res=self.recognize_speech_from_mic(recognizer, microphone)
                text=res["transcription"]
                if text==None:
                    play_audio('try_again.wav')
                    continue
                elif "结束对话" in text:
                    play_audio('goodbye.wav')
                    self.status="DETECTING"

                # 将识别的文本写入文件
                with open('Resource/text/question.txt', 'w', encoding='utf-8') as file:
                    file.write(text)
                
                # 3. 读取chatbot的回答
                play_waiting()
                #等待Response.txt发生更改
                
                with open('Resource/text/response.txt', 'r', encoding='utf-8') as file:
                    response_text = file.read()
                # 4. 调用tts的api获取输出语音
                synthesize_speech(response_text)
                logger.info('play response...')

                # 5. 播放回答
                play_audio('output.wav')
                logger.info('listening...')
                self.status="CHATING"

    def run_detect_wakeup_word(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        response=self.recognize_speech_from_mic(recognizer, microphone)
        #如果读取错误直接报错
        if(response["error"] != None):
            print(response["error"])
            return False
        #检测是否说了唤醒语句
        if self.awakeword in response["transcription"]:
            return True
        else:
            return False
        
    