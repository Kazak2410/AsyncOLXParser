import re
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import lxml


count_products = 0
most_expensive_product_price = 0
most_expensive_product_name = None
most_expensive_product_url = None
total_price_goods = 0
data_dict = []

async def get_page_data(session: aiohttp.ClientSession, page: int):
    global count_products, most_expensive_product_price, total_price_goods, most_expensive_product_name, most_expensive_product_url, data_dict

    headers = {
        'Accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    url = f'https://www.olx.ua/elektronika/kiev/?page={page}'

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')
        # get product information
        items = soup.find('div', class_='css-oukcj3').find_all('div', class_='css-1sw7q4x')

        for item in items:
            count_products += 1
            print(f'product {count_products} is done')
            product_name = item.find('h6', class_='css-16v5mdi er34gjf0').text
            product_price = ''.join(re.findall(r'\d+', item.find('p', class_='css-10b0gli er34gjf0').text))
            product_url = 'https://www.olx.ua' + item.find('a', class_='css-rc5s2u')['href']

            # if price is not negotiable
            if product_price:
                product_price = int(product_price)
                total_price_goods += product_price
                if most_expensive_product_price < product_price:
                    most_expensive_product_price = product_price
                    most_expensive_product_name = product_name
                    most_expensive_product_url = product_url

            data = {
                'product_name': product_name,
                'product_price': product_price,
                'product_url': product_url
            }
            data_dict.append(data)

            with open('data.json', 'w', encoding='utf-8') as json_file:
                json.dump(data_dict, json_file, indent=4, ensure_ascii=False)


async def gather_data():
    headers = {
        'Accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    url = 'https://www.olx.ua/elektronika/kiev/'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        # get the count of pages
        pages_count = soup.find('div', class_='css-4mw0p4').find_all('li')[-1].find('a', class_='css-1mi714g').text
        tasks = []
        # create event loop
        for page in range(1, int(pages_count) + 1):
            # get information from the page
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.run(gather_data())


if __name__ == '__main__':
    main()
    print(f"the most expensive product name: {most_expensive_product_name}")
    print(f"the most expensive product price: {most_expensive_product_price}")
    print(f"the most expensive product url: {most_expensive_product_url}")
    print(f"total count of products: {count_products}")
    print(f"average price of goods: {total_price_goods / count_products}")
    print(f"total price of goods: {total_price_goods}")
