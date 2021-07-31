import telegram

class telegram_post:
    def __init__(self):
        self.token = '1843659738:AAGmaISRmkyDReqdd72QoUaAJIdx-PfD2HI'

    def postToChannel(self, job_title, job_desc):
        # use token generated in first step
        bot = telegram.Bot(token=self.token)
        message = job_title+'\n\n'+job_desc
        # status = bot.send_message(chat_id="@blockchains_jobs", text=message, parse_mode=telegram.ParseMode.HTML)
        status = bot.send_message(chat_id="-1001576068728", text=message, parse_mode=telegram.ParseMode.HTML)
        # print(status)