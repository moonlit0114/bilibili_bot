
from .coinBot import BilibiliCoinBot
# 这里填入up主的uid
uid = ""

# 这里填写你自身的 cookies
cookies = {
}

def main():
    bot = BilibiliCoinBot(uid, cookies)
    bot.run()


if __name__ == "__main__":
    main()
