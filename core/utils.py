import datetime
from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from proxycurl_py.asyncio import Proxycurl
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY


def get_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Translate to English", callback_data="translate")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def update_text(message: Message, new_value: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(new_value)


async def get_letter(url):
    prompt = await get_info(url)

    client = AsyncOpenAI(
        api_key=OPENAI_API_KEY,
    )

    completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4",
    )
    letter = completion.choices[0].message.content
    return letter


async def get_info(url):
    proxycurl = Proxycurl()
    user = await proxycurl.linkedin.person.get(
        url=url,
        fallback_to_cache='on-error',
        use_cache='if-present',
        skills='exclude',
        inferred_salary='exclude',
        personal_email='include',
        personal_contact_number='exclude',
        twitter_profile_id='exclude',
        facebook_profile_id='exclude',
        github_profile_id='exclude',
        extra='exclude',
    )

    # Putting together the information
    experiences = [f"{experience['title']} in {experience['company']}" for experience in user["experiences"]]
    try:
        years_experience = datetime.date.today().year - user['experiences'][-1]['starts_at']['year']
    except:
        years_experience = 0

    try:
        email = user['personal_emails'][0]
    except:
        email = None

    education = [f"{education['degree_name']} from {education['school']}, described as {education['description']}" for
                 education in user["education"]]

    # Needed info
    '''
    print(user['full_name'])
    print(email)
    print(user['occupation'])
    print(user["headline"])
    print(user['summary'])
    print(years_experience)
    print(education)
    print(experiences)
    '''

    # Prompt for the model
    content = f'''Given the provided LinkedIn information for a person, create a proposal email on behalf of the company HappyAI, which specializes in implementing AI into business processes to increase profits, based on video.
        Here's the information:
        "Full name: {user['full_name']}. 
        Email: {email}.
        Current occupation: {user['occupation']};
        Profile's headline: {user["headline"]}.
        Person's profile summary: {user['summary']}.
        Years of experience: {years_experience}.
        Experiences: {experiences}.
        Education: {education}."
        Ignore null and blank contents and special characters in the provided information. If there's an email address in the provided information, put it before the letter in <> braces.
        '''

    return content
