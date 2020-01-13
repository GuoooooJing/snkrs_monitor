import time

import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

url = 'https://api.nike.com/snkrs/content/v1/?country=US&language=en&offset=0&orderBy=published'
webhook_url = 'your discord webhook url'


def check_update(data, previous):
    new_dict = {}
    extra_dict = {}
    new = set()
    for i in data:
        new.add(i['id'])
        if i['id'] in previous:
            continue
        elif i['interestId']:
            info = {}
            info['type'] = i['product']['productType']
            info['name'] = i['name']
            info['color'] = i['product']['colorDescription']
            info['price'] = i['product']['price']['msrp']
            info['image'] = i['imageUrl']
            info['date'] = i['product']['startSellDate']
            info['publishType'] = i['product']['publishType']
            new_dict[i['id']] = info
        else:
            info = {}
            info['name'] = i['name']
            info['image'] = i['imageUrl']
            info['date'] = i['publishedDate']
            info['desc'] = '\n'.join(i['tags'])
            extra_dict[i['id']] = info

    return new_dict, extra_dict, new


def update_discord(new, extra, webhook_url):
    webhook = DiscordWebhook(url=webhook_url)
    for i in new:
        embed = DiscordEmbed(title='{}({})'.format(new[i]['name'], new[i]['color']), description='id: {}'.format(i),
                             color=7395813, timestamp=new[i]['date'])

        embed.set_thumbnail(url=new[i]['image'])

        embed.set_footer(text="Lacuh time", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
        embed.set_image(url=new[i]['image'])
        embed.add_embed_field(name="Lauch Method", value="{}".format(new[i]['publishType']))
        embed.add_embed_field(name="Price", value="${}\n".format(new[i]['price']))
        embed.add_embed_field(name='Product Type', value=new[i]['type'])
        webhook.add_embed(embed)
        webhook.execute()
        webhook.remove_embed(0)
        time.sleep(3)
    for i in extra:
        embed = DiscordEmbed(title=extra[i]['name'], description='id: {}'.format(i),
                             color=7395813, timestamp=extra[i]['date'])
        embed.set_image(url=extra[i]['image'])
        embed.set_footer(text='Published time', icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
        embed.set_thumbnail(url=extra[i]['image'])
        embed.add_embed_field(name='detail', value=extra[i]['desc'])
        webhook.add_embed(embed)
        webhook.execute()
        webhook.remove_embed(0)
        time.sleep(3)


if __name__ == '__main__':
    previous = {}
    count = 0
    while True:
        count += 1
        count %= 100000
        print(count)
        jfile = requests.get(url).json()
        if 'threads' not in jfile:
            print(jfile)
            print('skip')
            continue
        data = jfile['threads']
        time.sleep(2)
        dic, extra, previous = check_update(data, previous)
        update_discord(dic, extra, webhook_url)
        print(len(dic))
