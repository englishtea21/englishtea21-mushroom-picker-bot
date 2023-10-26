import torch
from torchvision import transforms
from sklearn.preprocessing import LabelEncoder
import pickle
from bs4 import BeautifulSoup
from PIL import Image

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode

import aiohttp

from os import getenv
from dotenv import load_dotenv

import text
import re
from urllib.parse import quote_plus, quote

load_dotenv()

"""
used utils
"""


class NNProcessor:
    """
    Neural network predict class
    """

    _TRAIN_RESCALE_SIZE = 640
    # к этому размеру мы приводим картинки train'а
    # для дальнейшего рандомного обрезания под размер RESCALE_SIZE для аугментации данных
    _RESCALE_SIZE = 512

    def __init__(self, PATH_TO_MODEL, PATH_TO_ENCODER):
        self.nn_model = torch.load(PATH_TO_MODEL, map_location=torch.device("cpu"))

        with open(PATH_TO_ENCODER, "rb") as f:
            # dict1 = pickle.load(f)
            self.label_encoder = pickle.load(f)

        self.photo_transformations = transforms.Compose(
            [
                transforms.Resize(self._RESCALE_SIZE),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def predict(self, img: Image):
        """
        model predict method
        """

        """
        convert input img to conventional format
        """
        jpg_image = img.convert("RGB")
        """
        make central cropping and preprocessing conventional to neural network
        """
        jpg_image = transforms.Compose(
            [transforms.ToTensor(), transforms.CenterCrop(max(jpg_image.size))]
        )(jpg_image)
        jpg_image = self.photo_transformations(jpg_image)
        jpg_image = jpg_image.unsqueeze(0)  # batch dimension adding

        # get nn outputs
        with torch.no_grad():
            output = self.nn_model(jpg_image)

        # get top 3 of predictions
        top_predicted_classes = torch.topk(output.flatten(), 3).indices

        # decoding predictions
        return self.label_encoder.inverse_transform(top_predicted_classes)


class ResultComposer:
    """
    Result text message composer
    """

    def __init__(self):
        pass

    async def compose_result(self, mushrooms_list):
        mushrooms_list = list(
            map(lambda s: re.sub(r"[^a-zA-Z]", " ", s).title(), mushrooms_list)
        )

        items = [
            text.text_templates["RESULT_MESSAGE_TEMPLATES"]["RESULT_BULLET_LI"].format(
                *(
                    text.text_templates["RESULT_MESSAGE_TEMPLATES"][
                        "LINK_TEMPLATE"
                    ].format(getenv("SEARCH_ENGINE").format(quote(mushroom)), mushroom),
                    text.text_templates["RESULT_MESSAGE_TEMPLATES"][
                        "PLATFORM_SEARCH_TEMPLATE"
                    ].format(getenv("PLATFORM_SEARCH").format(quote(mushroom))),
                )
            )
            + await self._compose_article_answer(mushroom)
            for mushroom in mushrooms_list
        ]

        bullet_list = "\n\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
        return (
            text.text_templates["RESULT_MESSAGE_TEMPLATES"]["RESULT_TEMPLATE"]
            + bullet_list
        )

    async def _compose_article_answer(self, mushroom):
        """
        get query link on platform
        """

        article = await self._brief_on_platform(mushroom)

        answer = (
            text.text_templates["RESULT_MESSAGE_TEMPLATES"]["FIRST_ARTICLE"].format(
                article
            )
            if article is not None
            else text.text_templates["RESULT_MESSAGE_TEMPLATES"]["NOT_FOUND"]
        )

        return answer

    async def _brief_on_platform(self, mushroom):
        """
        get 1st link among searched on platform
        """
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(
                getenv("PLATFORM_SEARCH").format(quote_plus(mushroom))
            ) as resp:
                body = await resp.text()
                soup = BeautifulSoup(body, "html.parser")

                try:
                    top_link = soup.select_one("span.taxon a").attrs["href"]
                except AttributeError:
                    top_link = None

                return (
                    getenv("PLATFORM_WEBSCRAPPING") + "/" + top_link
                    if top_link is not None
                    else None
                )


nn_processor = NNProcessor(getenv("PATH_TO_MODEL"), getenv("PATH_TO_ENCODER"))

result_composer = ResultComposer()

bot = Bot(token=getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
