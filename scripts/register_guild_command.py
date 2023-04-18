import requests
import os
# import re
import regex

my_application_id = os.getenv("DISCORD_APPLICATION_ID")
guild_id = os.getenv("DISCORD_GUILD_ID")
my_bot_token = os.environ.get("DISCORD_BOT_TOKEN")


def create_command(name: str, type: int, description: str = None, *, name_localizations: dict = None, description_localizations: dict = None, options: list = None) -> int:
    """
    Guild Commandを作成する。
    :param name: コマンドの名前(ユーザーに表示される。slash commandではこれを入力して使う。).
        regex: ^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$
    :param name_localizations: 名前のローカライズ(slash commandでは入力するコマンドがこれになる。).
    :param type: コマンドのタイプ.
        1: Slash Command
        2: User Command
        3: Message Command
    :param description: コマンドの説明(slashcommand(type:1)の場合のみ必要).
    :param description_localizations: 説明のローカライズ.
        {"ja":"Description in Japanese", ...}
    :return: コマンドのID
    """

    if not regex.match(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", name):
        raise ValueError("name is invalid")
    if type not in [1, 2, 3]:
        raise ValueError("type is invalid")
    if description is not None and len(description) > 100:
        raise ValueError("description is too long")
    if description_localizations is not None:
        for k, v in description_localizations.items():
            if len(v) > 100:
                raise ValueError(f"description_localizations[{k}] is too long")
    if name_localizations is not None:
        for k, v in name_localizations.items():
            if not regex.match(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", v):
                raise ValueError(f"name_localizations[{k}] is invalid")
    if options is not None:
        for option in options:
            if "name" not in option or "type" not in option or "description" not in option:
                raise ValueError("option is invalid")
            elif not regex.match(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", option.get("name", "")):
                raise ValueError("option name is too long")
            elif not 1 <= option.get("type", 0) <= 11:
                raise ValueError("option type is invalid")
            elif not option.get("description", "") or len(option.get("description", "")) > 100:
                raise ValueError("option description is invalid")

    payload = dict()
    payload["name"] = name
    payload["type"] = type
    if description is not None and type == 1:
        payload["description"] = description
    if description_localizations is not None and type == 1:
        payload["description_localizations"] = description_localizations
    if name_localizations is not None:
        payload["name_localizations"] = name_localizations
    if options is not None:
        payload["options"] = options

    url = f"https://discord.com/api/v10/applications/{my_application_id}/guilds/{guild_id}/commands"

    headers = {
        "Authorization": f"Bot {my_bot_token}"
    }

    r = requests.post(url, headers=headers, json=payload)
    status = r.status_code
    if status != requests.codes.created and status != requests.codes.ok:
        raise Exception(f"status code: {status}\n{r.content}")
    return int(r.json()["id"])


if __name__ == "__main__":
    # コマンドを作成する
    command_id = create_command("feedback", 1, "provide feedback", description_localizations={"ja": "フィードバックを送る。", }, options=[
            {"name": "title", "type": 3, "description": "title", "description_localizations": {"ja": "タイトル"}, "required": True},
            {"name": "message", "type": 3, "description": "message to send", "description_localizations": {"ja": "送信するメッセージ。"}, "required": True},
            {"name": "file", "type": 11, "description": "file to send", "description_localizations": {"ja": "添付するファイル。"}, "required": False}
        ])
    print(command_id)
