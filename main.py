import time
import requests
import discord
from discord import ui, app_commands
from discord.ui import Select, View
from discord.ext import commands
import datetime
from discord import Color as c
import asyncio
import pickle
import os
from bs4 import BeautifulSoup
from pytz import timezone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

def res(ins):
    global result
    url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query={ins} 급식식단"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    par = soup.find_all('div', {'class':'timeline_list open'})

    #or div in par:
    #    a = "".join(div.text)
    #    print(a)
    #    b = a.split('          ')
    #    print(b)

    meal = "".join([div.text for div in soup.find_all('div', {'class':'timeline_list open'})])
    mealres = meal.replace('          ', '\n\n')
    mealres = mealres.replace('       ', '')
    mealres = mealres.replace(' ', '\n')
    mealres = mealres.replace('\n\n\n', '')
    result = mealres.replace('TODAY', '')
    return result

cred_path = "notificationtestapp-662be-firebase-adminsdk-zoff4-0f8d1ee7b3.json"
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

registration_token = "YOUR_TOKEN" # replace with your firebase registration_token
message = messaging.Message(
    notification=messaging.Notification(
        title='알리미 봇 초기 설정',
        body='알리미 봇 활성화 완료!'
    ),
    token=registration_token,
    )


response = messaging.send(message)
print('초기설정 완료:', response)

MY_GUILD = discord.Object(id=YOUR_ID)  # replace with your guild id

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync()

intents = discord.Intents.default()
intents.members = True
client = MyClient(intents=intents)

@client.event
async def on_guild_join(guild):
    print(f'{guild}에 접속하였어요!')
    channel2 = client.get_channel(log_channel) # replace with your log channel
    embed = discord.Embed(title=":up: 알리미 로그",
                          description=f"{guild}에 접속하였습니다!",
                          color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
    embed.set_footer(text="제작자 : _Richardo | 연락 : richardo@richardo.net")
    await channel2.send(embed=embed)
    try:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(title=":wave: 알리미",
                                      description="알리미를 사용해주셔서 감사합니다!\n알리미의 기본적인 사용법과 연동 방법은 </도움말:1016630692160995379>을 참조해주세요!",
                                      color=0x0000ff, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
                embed.set_footer(text="제작자 : _Richardo | 연락 : richardo@richardo.net")
                await channel.send(embed=embed)
            break
    except:
        None

@client.event
async def on_ready():
    channel = client.get_channel(notify_channel) # replace with your notify channel
    embed = discord.Embed(title=":up: 알리미",
                          description="알리미 활성화 완료!",
                          color=0x0000ff, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
    embed.set_footer(text="제작자 : _Richardo | 연락 : richardo@richardo.net")
    await channel.send(embed=embed)
    print(f'봇 준비 완료 : {client.user} (ID: {client.user.id})')
    print(f'봇은 현재 {len(client.guilds)}개의 서버에 연결되어 있습니다. 리스트 : ')
    print('')
    channel2 = client.get_channel(log_channel) # replace with your log channel
    embed = discord.Embed(title=":up: 알리미 로그",
                          description=f"알리미 활성화 완료 : {client.user} (ID: {client.user.id}, 봇은 현재 {len(client.guilds)}개의 서버에 연결되어 있습니다. 리스트 :",
                          color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
    a = 0
    for server in client.guilds:
        a += 1
        embed.add_field(name=f'{a}', value=f'{server.name}')
        print(server.name)

    #print(data.name)
    print('------')

    embed.set_footer(text="제작자 : _Richardo | 연락 : richardo@richardo.net")
    await channel2.send(embed=embed)
    game = discord.Game("알리미 봇 v1 출시! 원스토어 '알리미 수신 앱' | 도움말은 '/도움말'")
    await client.change_presence(status=discord.Status.online, activity=game)
    while True:
        game1 = discord.Game(f"원스토어 '알리미 수신 앱' | 도움말은 '/도움말 | 현재 {len(client.guilds)}개의 서버에서 활약중이에요!")
        await client.change_presence(status=discord.Status.online, activity=game1)
        await asyncio.sleep(15)

class button_view(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.member)

    @discord.ui.button(label = "수신 성공", style=discord.ButtonStyle.green, custom_id="callanw")
    async def callanw(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        interaction.message.author = interaction.user
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()
        if retry:
            wait = round(retry)
            embed = discord.Embed(title=":bell: 알리미", description=f"{wait}초 후 다시시도해주세요.", color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            return await interaction.followup.send(embed=embed, ephemeral=True)

        with open(f"DB/{interaction.user.id}.bin", "rb") as f:
            user_data = pickle.load(f)

        embed = discord.Embed(title=":white_check_mark: 알리미",
                              description=f"토큰 등록 완료!\n등록된 토큰 : ||{user_data[str('token')]}||", color=0x00ff00,
                              timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, ephemeral=True)


    @discord.ui.button(label="수신 실패", style=discord.ButtonStyle.green, custom_id="callcancel")
    async def callcanel(self, interaction: discord.Interaction, button: discord.ui.Button):
        interaction.message.author = interaction.user
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()
        if retry:
            await interaction.response.defer(ephemeral=True)
            wait = round(retry)
            embed = discord.Embed(title=":bell: 알리미", description=f"{wait}초 후 다시시도해주세요.", color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            return await interaction.followup.send(embed=embed, ephemeral=True)

        os.remove(f"DB/{interaction.user.id}.bin")
        embed = discord.Embed(title=":white_check_mark: 알리미",
                              description=f"알리미 서버에 저장된 토큰을 삭제했어요! 다시 등록해주세요!", color=0x00ff00,
                              timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command()
@app_commands.checks.cooldown(3, 30, key=lambda i: (i.guild_id, i.user.id))
async def 도움말(interaction: discord.Interaction):
    """도움말을 표출합니다."""
    await interaction.response.defer(ephemeral=False)
    select = Select(options=[
        discord.SelectOption(label="연동 방법", emoji="🔗", description="알리미 봇과 알리미 앱을 연동하는 방법을 표출합니다."),
        discord.SelectOption(label="호출 방법", emoji="💬", description="알리미 봇을 통해 유저를 호출하는 방법을 표출합니다."),
    ])
    async def q_callback(interaction: discord.Interaction):
        if select.values[0] == "연동 방법":
            embed = discord.Embed(title=":information_source: 알리미 도움말",
                                  description="알리미의 사용법을 안내합니다. [알리미 서포트 서버](https://discord.gg/2XrQm4u5tN)",
                                  color=0x0000ff, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            embed.add_field(name="알리미 앱 등록법",
                            value=f"알리미 봇을 등록하시려면 아래와 같이 행동해주세요!\n1. 원스토어에서 '알리미 수신 앱' 검색 후 노출되는 앱 다운로드.\n2. 앱내 토큰 표시 필드에서 전체 선택 후 복사.\n3. 디스코드 알리미 봇 '/토큰등록' 명령어를 사용하여 토큰 등록 후 사용!")
            embed.set_footer(text="제작자 : _Richardo | 연락 : richardo@richardo.net")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        if select.values[0] == "호출 방법":
            embed = discord.Embed(title=":information_source: 알리미 도움말",
                                  description="알리미의 사용법을 안내합니다. [알리미 서포트 서버](https://discord.gg/2XrQm4u5tN)",
                                  color=0x0000ff, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            embed.add_field(name="알리미 사용법",
                            value=f"알리미를 사용하시려면 아래와 같이 행동해주세요!\n1. /호출 명령어를 통해 원하는 유저를 호출할 수 있습니다!\n2. 또는 /메시지를 통해 간단한 메시지와 함께 유저를 호출할 수 있습니다!\n3. 아니면 호출을 원하는 유저를 우클릭 -> 앱 -> 호출하기를 통해서도 호출할 수 있습니다!")
            embed.set_footer(text="제작자 : _Richardo | 연락 : richardo@richardo.net")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    select.callback = q_callback
    view = View()
    view.add_item(select)
    embed = discord.Embed(title=":information_source: 알리미 도움말", description="아래 메뉴에서 궁금하신 내용을 선택해주세요! [알리미 서포트 서버](https://discord.gg/2XrQm4u5tN)", color=0x0000ff, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
    embed.set_footer(text="제작자 : _Richardo | 연락 : richardo@richardo.net")
    await interaction.followup.send(embed=embed, ephemeral=False, view=view)

@client.tree.command()
@app_commands.checks.cooldown(3, 30, key=lambda i: (i.guild_id, i.user.id))
@app_commands.describe(토큰='알리미 앱에서 표출되는 토큰을 입력해주세요.')
async def 토큰등록(interaction: discord.Interaction, 토큰: str):
    """알리미 앱과 알리미 봇을 연동합니다."""
    await interaction.response.defer(ephemeral=True)

    try:
        with open(f"DB/{interaction.user.id}.bin", "rb") as f:
            user_data = pickle.load(f)
        embed = discord.Embed(title=":x: 알리미 에러", description=f"이미 토큰이 등록된 아이디입니다. '/토큰해제' 명령어를 사용해주세요.\n등록된 토큰 : ||{user_data[str('token')]}||", color=0xff0000, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, ephemeral=True)
    except FileNotFoundError:
        with open(f"DB/{interaction.user.id}.bin", "wb+") as f:
            user_data = dict()
            user_data[str("token")] = str(토큰)
            pickle.dump(user_data, f)
        now = round(time.time())
        embed = discord.Embed(title=":white_check_mark: 알리미",
                              description=f"알림을 전송하는 중...\n전송 소요 시간 : <t:{now}:R>|`30초 전`\n알리미 서버는 ntp 서버로 `time.bora.net`을 사용하고 있습니다.",
                              color=0x00ff00,
                              timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        embed.set_footer(text="전송까지 최대 1분가량 소요될 수 있습니다. 잠시 기다려주세요.")
        await interaction.followup.send(embed=embed, ephemeral=True)
        registration_token = user_data[str("token")]
        message = messaging.Message(
            notification=messaging.Notification(
                title='알리미 메시지 수신 테스트',
                body='수신이 되었다면 디스코드에서 버튼을 눌러주세요!'
            ),
            token=registration_token,
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)

        embed = discord.Embed(title=":white_check_mark: 알리미",
                              description=f"아래 토큰으로 메시지를 전송했습니다! 수신이 잘 되었나요?\n등록된 토큰 : ||{user_data[str('token')]}||", color=0x00ff00,
                              timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, view = button_view(), ephemeral=True)
    except:
        os.remove(f"DB/{interaction.user.id}.bin")
        embed = discord.Embed(title=":x: 알리미 에러", description=f"파일 삭제 완료! 다시 등록해주세요 ( 에러 해결 )", color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command()
@app_commands.checks.cooldown(3, 30, key=lambda i: (i.guild_id, i.user.id))
async def 토큰해제(interaction: discord.Interaction):
    """알리미 앱과 알리미 봇의 연동을 해제합니다."""
    await interaction.response.defer(ephemeral=True)
    try:
        with open(f"DB/{interaction.user.id}.bin", "rb") as f:
            user_data = pickle.load(f)
        os.remove(f"DB/{interaction.user.id}.bin")
        embed = discord.Embed(title=":bell: 알리미", description=f"알리미의 연결을 해제하였어요!\n다음에 또 만나요!!", color=0x0000ff,
                              timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, ephemeral=True)
    except FileNotFoundError:
        embed = discord.Embed(title=":x: 알리미 에러", description=f"알리미에 등록된 토큰이 없습니다! 토큰 등록을 먼저 해주세요. '/토큰등록'", color=0xff0000,
                              timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command()
@app_commands.checks.cooldown(3, 30, key=lambda i: (i.guild_id, i.user.id))
@app_commands.describe(학교='급식 조회를 원하는 학교를 입력해주세요.')
async def 급식(interaction: discord.Interaction, 학교: str):
    """원하는 학교의 급식 정보를 표출합니다."""
    await interaction.response.defer(ephemeral=False)
    embed = discord.Embed(title=f":fork_knife_plate: {학교} 급식 정보", description=f"{res(f'{학교}')}",
                          color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
    await interaction.followup.send(embed=embed, ephemeral=False)

@client.tree.command()
@app_commands.checks.cooldown(3, 30, key=lambda i: (i.guild_id, i.user.id))
async def 정보(interaction: discord.Interaction):
    """봇의 정보를 표출합니다."""
    await interaction.response.defer(ephemeral=False)
    embed = discord.Embed(title=f":bell: 알리미", description=f"[알리미 서포트 서버](https://discord.gg/2XrQm4u5tN)",
                          color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
    embed.add_field(name="봇 개발자", value="제작자 : _Richardo")
    embed.add_field(name="연락", value='richardo@richardo.net')
    embed.add_field(name="개발 언어", value='Python ( dpy 2.0 )')
    embed.add_field(name="봇 출품 일시", value='2022.09.06')
    embed.set_footer(text='알리미')
    await interaction.followup.send(embed=embed, ephemeral=False)

@client.tree.command()
@app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
async def 유저목록(interaction: discord.Interaction):
    """서버에서 알리미를 사용하고 있는 유저 리스트를 출력합니다."""

    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title=":bell: 알리미", description=f"현재 서버에서 알리미를 사용하고 있는 유저 목록", color=0x0000ff,
                          timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
    a = 0
    for member in interaction.guild.members:
        try:
            with open(f"DB/{member.id}.bin", "rb") as f:
                user_data = pickle.load(f)
            a += 1
            embed.add_field(name=f'{a}', value=f'{member}')

        except FileNotFoundError:
            None
    embed.set_footer(text=f'알리미를 사용하고 있는 유저 수 : {a}')
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command()
@app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
@app_commands.describe(유저='호출할 유저를 선택해주세요.')
async def 호출(interaction: discord.Interaction, 유저: discord.Member):
    """특정 유저를 호출합니다."""

    await interaction.response.defer(ephemeral=True)
    try:
        with open(f"DB/{유저.id}.bin", "rb") as f:
            user_data = pickle.load(f)
        registration_token = user_data[str("token")]
        message = messaging.Message(
            notification=messaging.Notification(
                title='알리미 호출!',
                body=f'{interaction.user.name} 님이 호출하셨어요!'
            ),
            token=registration_token,
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)

        embed = discord.Embed(title=":bell: 호출 성공!", description=f"{유저.name} 님에게 알리미 알림을 전송하였습니다!",
                              color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))

        embed.set_footer(text="알림 전송에는 최대 1분까지 소요될 수 있습니다.")
        await interaction.followup.send(embed=embed, ephemeral=True)
    except FileNotFoundError:
        try:
            dm = await 유저.create_dm()
            embed = discord.Embed(title=":bell: 알리미 호출", description=f"{interaction.user.name} 님이 호출하였어요!", color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await dm.send(embed=embed)
            embed = discord.Embed(title=":warning: 알리미 주의", description=f"해당 유저는 알리미 앱을 등록하지 않아 DM으로 호출하였어요!",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            embed = discord.Embed(title=":x: 알리미 경고", description=f"해당 유저는 알리미 앱을 등록하지 않았어요!\nDM으로 호출을 시도하였으나, 실패하였어요.",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        try:
            dm = await 유저.create_dm()
            embed = discord.Embed(title=":bell: 알리미 호출", description=f"{interaction.user.name} 님이 호출하였어요!\n알리미 봇에 등록되어있는 토큰이 바르지 않습니다! 다시 </토큰해제:1016305864820404284> 후 재등록해주세요!", color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await dm.send(embed=embed)
            embed = discord.Embed(title=":warning: 알리미 주의", description=f"해당 유저는 알리미 앱을 등록하였지만 알리미 앱과 알리미 봇간의 토큰이 일치하지 않아 DM으로 호출하였어요!",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
        except AttributeError:
            embed = discord.Embed(title=":x: 알리미 경고", description=f"해당 유저는 알리미 앱을 등록하였지만 알리미 앱과 알리미 봇간의 토큰이 일치하지 않아요!\nDM으로 호출을 시도하였으나, 실패하였어요.",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.CommandOnCooldown):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.defer(ephemeral=True)
        wait = round(error.retry_after)
        embed = discord.Embed(title=":bell: 쿨타임", description=f"{wait}초 후 다시시도해주세요.", color=0xff0000, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        raise error

@client.tree.command()
@app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
@app_commands.describe(유저='호출할 유저를 선택해주세요.',
                       메시지='전달할 메시지를 입력해주세요.'
                       )
async def 메시지(interaction: discord.Interaction, 유저: discord.Member, 메시지: str):
    """메시지와 함께 특정 유저를 호출합니다!"""

    await interaction.response.defer(ephemeral=True)
    try:
        with open(f"DB/{유저.id}.bin", "rb") as f:
            user_data = pickle.load(f)
        registration_token = user_data[str("token")]
        message = messaging.Message(
            notification=messaging.Notification(
                title='알리미 호출!',
                body=f'{interaction.user.name} 님이 호출하셨어요! 호출 내용 : {메시지}'
            ),
            token=registration_token,
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)

        embed = discord.Embed(title=":bell: 호출 성공!", description=f"{유저.name} 님에게 알리미 알림을 전송하였습니다!\n호출 내용 : ||{메시지}||",
                              color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))

        embed.set_footer(text="알림 전송에는 최대 1분까지 소요될 수 있습니다.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    except FileNotFoundError:
        try:
            dm = await 유저.create_dm()
            embed = discord.Embed(title=":bell: 알리미 호출", description=f"{interaction.user.name} 님이 호출하였어요!\n호출 내용 : {메시지}", color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await dm.send(embed=embed)
            embed = discord.Embed(title=":warning: 알리미 주의", description=f"해당 유저는 알리미 앱을 등록하지 않아 DM으로 호출하였어요!\n호출 내용 : ||{메시지}||", color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            embed = discord.Embed(title=":x: 알리미 경고", description=f"해당 유저는 알리미 앱을 등록하지 않았어요!\nDM으로 호출을 시도하였으나, 실패하였어요.",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)

    except:
        try:
            dm = await 유저.create_dm()
            embed = discord.Embed(title=":bell: 알리미 호출", description=f"{interaction.user.name} 님이 호출하였어요!\n알리미 봇에 등록되어있는 토큰이 바르지 않습니다! 다시 </토큰해제:1016305864820404284> 후 재등록해주세요!", color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await dm.send(embed=embed)
            embed = discord.Embed(title=":warning: 알리미 주의", description=f"해당 유저는 알리미 앱을 등록하였지만 알리미 앱과 알리미 봇간의 토큰이 일치하지 않아 DM으로 호출하였어요!",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
        except AttributeError:
            embed = discord.Embed(title=":x: 알리미 경고", description=f"해당 유저는 알리미 앱을 등록하였지만 알리미 앱과 알리미 봇간의 토큰이 일치하지 않아요!\nDM으로 호출을 시도하였으나, 실패하였어요.",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command()
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
async def 핑(interaction: discord.Interaction):
    """봇의 핑을 출력합니다."""
    before = time.monotonic()
    await interaction.response.defer(ephemeral=False)
    lat2 = (time.monotonic() - before) * 1000
    lat = round(lat2, 1)
    ping = round(client.latency * 1000)
    if ping >= 0 and ping <= 100:
        st = "🔵 매우 좋음"
        embed = discord.Embed(title=f"🏓 퐁!", color=c.blurple(), timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        embed.add_field(name="지연시간", value=f'{lat}ms', inline=True)
        embed.add_field(name="API 지연시간", value=f'{ping}ms\n{st}', inline=True)
        await interaction.followup.send(embed=embed, ephemeral=False)
    elif ping >= 101 and ping <= 200:
        st = "🟢 좋음"
        embed = discord.Embed(title=f"🏓 퐁!", color=c.blurple(), timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        embed.add_field(name="지연시간", value=f'{lat}ms', inline=True)
        embed.add_field(name="API 지연시간", value=f'{ping}ms\n{st}', inline=True)
        await interaction.followup.send(embed=embed, ephemeral=False)
    elif ping >= 201 and ping <= 500:
        st = "🟡 보통"
        embed = discord.Embed(title=f"🏓 퐁!", color=c.blurple(), timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        embed.add_field(name="지연시간", value=f'{lat}ms', inline=True)
        embed.add_field(name="API 지연시간", value=f'{ping}ms\n{st}', inline=True)
        await interaction.followup.send(embed=embed, ephemeral=False)
    elif ping >= 501 and ping <= 1000:
        st = "🟠 느림"
        embed = discord.Embed(title=f"🏓 퐁!", color=c.blurple(), timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        embed.add_field(name="지연시간", value=f'{lat}ms', inline=True)
        embed.add_field(name="API 지연시간", value=f'{ping}ms\n{st}', inline=True)
        await interaction.followup.send(embed=embed, ephemeral=False)
    elif ping >= 1000:
        st = "🔴 매우 느림"
        embed = discord.Embed(title=f"🏓 퐁!", color=c.blurple(), timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
        embed.add_field(name="지연시간", value=f'{lat}ms', inline=True)
        embed.add_field(name="API 지연시간", value=f'{ping}ms\n{st}', inline=True)
        await interaction.followup.send(embed=embed, ephemeral=False)

@client.tree.context_menu(name='호출하기')
async def open_bell_context_menu(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    try:
        with open(f"DB/{member.id}.bin", "rb") as f:
            user_data = pickle.load(f)
        registration_token = user_data[str("token")]
        message = messaging.Message(
            notification=messaging.Notification(
                title='알리미 호출!',
                body=f'{interaction.user.name} 님이 호출하셨어요!'
            ),
            token=registration_token,
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)

        embed = discord.Embed(title=":bell: 호출 성공!", description=f"{member.name} 님에게 알리미 알림을 전송하였습니다!",
                              color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))

        embed.set_footer(text="알림 전송에는 최대 1분까지 소요될 수 있습니다.")
        await interaction.followup.send(embed=embed, ephemeral=True)
    except FileNotFoundError:
        try:
            dm = await member.create_dm()
            embed = discord.Embed(title=":bell: 알리미 호출", description=f"{interaction.user.name} 님이 호출하였어요!",
                                  color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await dm.send(embed=embed)
            embed = discord.Embed(title=":warning: 알리미 주의", description=f"해당 유저는 알리미 앱을 등록하지 않아 DM으로 호출하였어요!",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            embed = discord.Embed(title=":x: 알리미 경고", description=f"해당 유저는 알리미 앱을 등록하지 않았어요!\nDM으로 호출을 시도하였으나, 실패하였어요.",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        try:
            dm = await member.create_dm()
            embed = discord.Embed(title=":bell: 알리미 호출", description=f"{interaction.user.name} 님이 호출하였어요!\n알리미 봇에 등록되어있는 토큰이 바르지 않습니다! 다시 </토큰해제:1016305864820404284> 후 재등록해주세요!", color=0x00ff00, timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await dm.send(embed=embed)
            embed = discord.Embed(title=":warning: 알리미 주의", description=f"해당 유저는 알리미 앱을 등록하였지만 알리미 앱과 알리미 봇간의 토큰이 일치하지 않아 DM으로 호출하였어요!",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)
        except AttributeError:
            embed = discord.Embed(title=":x: 알리미 경고", description=f"해당 유저는 알리미 앱을 등록하였지만 알리미 앱과 알리미 봇간의 토큰이 일치하지 않아요!\nDM으로 호출을 시도하였으나, 실패하였어요.",
                                  color=0xff0000,
                                  timestamp=datetime.datetime.now(timezone('Asia/Seoul')))
            await interaction.followup.send(embed=embed, ephemeral=True)

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send("슬래시 커맨드를 이용해주세요! '/도움말'")

client.run('BOT_TOKEN') # replace with your bot token

