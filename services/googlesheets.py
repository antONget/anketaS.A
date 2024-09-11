import gspread
import logging

gp = gspread.service_account(filename='services/kingdom.json')
gsheet = gp.open('АНКЕТА')
sheet = gsheet.worksheet("Лист1")


async def append_row(order: list) -> None:
    logging.info(f'append_row')
    sheet.append_row(order)
