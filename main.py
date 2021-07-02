import os
import re
import sys

import discord
from loguru import logger


class HelloClient(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.all()
        super().__init__(intents=intents, *args, **kwargs)

    async def on_ready(self):
        logger.info(f'{self.user} | Ready!')

    async def on_message(self, ctx):
        if ctx.author.id != int(os.getenv('AUTHOR_ID')):
            return

        if ctx.content == '!nicknamebye':
            logger.info('Closed by command')
            await self.close()

    async def on_member_update(self, before, after):
        logger.info(f'{before}, {after}')
        if before.display_name != after.display_name:
            logger.info(f'{before.display_name} -> {after.display_name}')

        valid_after = valid_nick(after.display_name)

        role = None
        for r in after.guild.roles:
            if r.name == '大神':
                role = r

        if role is None:
            return

        for ch in after.guild.channels:
            if ch.name == 'hello-world':
                break

        if valid_after:
            if role not in after.roles:
                await after.add_roles(role)
                msg = f'{after.mention} 變成 {role.mention} 了！'
                await ch.send(msg)
                logger.info(msg)
        else:
            if role in after.roles:
                await after.remove_roles(role)
                msg = f'{after.mention} 不當 {role.mention} 了 QQ'
                await ch.send(msg)
                logger.info(msg)

    async def on_member_join(self, member):
        logger.info(f'{member.display_name} join!')
        valid = valid_nick(member.display_name)

        for r in member.guild.roles:
            if r.name == '大神':
                role = r

        for ch in member.guild.channels:
            if ch.name == 'hello-world':
                break

        if valid:
            await member.add_roles(role)
            msg = f'{member.mention} 變成 {role.mention} 了！'
            await ch.send(msg)
            logger.info(msg)

def valid_nick(s):
    if s is None:
        return False

    if re.match(r'[\dA-Z]{8} .+', s):
        return True

    return False

def set_logger():
    log_format = (
        '{time:YYYY-MM-DD HH:mm:ss.SSSSSS} | '
        '<lvl>{level: ^9}</lvl> | '
        '{message}'
    )
    logger.add(sys.stderr, level='INFO', format=log_format)
    logger.add(
        f'./logs/system.log',
        rotation='1 day',
        retention='7 days',
        level='INFO',
        encoding='UTF-8',
        format=log_format
    )

if __name__ == '__main__':
    set_logger()
    token = os.getenv('TOKEN')
    HelloClient().run(token)
