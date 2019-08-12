from tqdm import tqdm
from datetime import datetime
import requests


class _TelegramIO():
    TIMEOUT = 5

    def __init__(self, token, chat_id, show_last_update=True, proxy_url=None):
        self.token = token
        self.chat_id = chat_id
        self.text = self.prev_text = '<< Init tg_tqdm bar >>'
        self.proxies = dict(https=proxy_url) if proxy_url else None
        self.requests_session = requests.Session()
        r = self.requests_session.post('https://api.telegram.org/bot%s/sendMessage' % self.token,
                          json=dict(text=self.text, chat_id=self.chat_id),
                          proxies=self.proxies, timeout=_TelegramIO.TIMEOUT)
        self.message_id = r.json()['result']['message_id']
        self.show_last_update = show_last_update

    def write(self, s):
        new_text = s.strip().replace('\r', '')
        if len(new_text) != 0:
            self.text = new_text

    def update_message(self):
        try:
            updated_text = self.text + '\nLast update: {}'.format(datetime.now()) if self.show_last_update else ''
            self.requests_session.post('https://api.telegram.org/bot%s/editMessageText' % self.token,
                          json=dict(text=updated_text, chat_id=self.chat_id, message_id=self.message_id),
                          proxies=self.proxies, timeout=_TelegramIO.TIMEOUT)
        except Exception as e:
            print(e)

    def flush(self):
        if self.prev_text != self.text:
            if '%' in self.text:
                self.update_message()
                self.prev_text = self.text


def tg_tqdm(iterable, token, chat_id, show_last_update=True,
            desc=None, total=None, leave=True, ncols=None, mininterval=1.0, maxinterval=10.0,
            miniters=None, ascii=False, disable=False, unit='it',
            unit_scale=False, dynamic_ncols=False, smoothing=0.3,
            bar_format=None, initial=0, position=None, postfix=None,
            unit_divisor=1000, gui=False, proxy_url=None, **kwargs):
    """
    Decorate an iterable object, returning an iterator which acts exactly
    like the original iterable, but send to Telegram a dynamically updating
    progressbar every time a value is requested.

        Parameters
        ----------
        iterable  : iterable, required
            Iterable to decorate with a progressbar.
            Leave blank to manually manage the updates.
        token  : string, required
            Token of your telegram bot

        chat_id  : int, required
            Chat ID where information will be sent about the progress

        show_last_update  : bool, optional [default: True]
            Should I show the time-date of the last change in the progress bar?

        desc, total, leave, ncols, ... :
            Like in tqdm

        proxy_url  : string, optional [default: None]
            url for telebot proxy, 'socks5://username:password@ip:port' for example
    """
    tg_io = _TelegramIO(token, chat_id, show_last_update, proxy_url)
    return tqdm(iterable=iterable,
                desc=desc,
                total=total,
                leave=leave,
                file=tg_io,
                ncols=ncols,
                mininterval=mininterval,
                maxinterval=maxinterval,
                miniters=miniters,
                ascii=ascii,
                disable=disable,
                unit=unit,
                unit_scale=unit_scale,
                dynamic_ncols=dynamic_ncols,
                smoothing=smoothing,
                bar_format=bar_format,
                initial=initial,
                position=position,
                postfix=postfix,
                unit_divisor=unit_divisor,
                gui=gui,
                **kwargs)
