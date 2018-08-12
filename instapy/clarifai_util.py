"""Module which handles the clarifai api and checks
the image for invalid content"""
from clarifai.rest import ClarifaiApp


def check_image(browser, clarifai_api_key, img_tags, img_tags_skip, logger, full_match=False, picture_url=None):
    """Uses the link to the image to check for invalid content in the image"""
    clarifai_api = ClarifaiApp(api_key=clarifai_api_key)
    # set req image to given one or get it from current page
    if picture_url is None:
        img_link = get_imagelink(browser)
    else:
        img_link = picture_url
    # Uses Clarifai's v2 API
    model = clarifai_api.models.get('general-v1.3')
    # image = ClImage(url=img_link)

    logger.info('Predicting clarifai with URL %s', img_link)

    result = model.predict_by_url(url=img_link)

    clarifai_tags = [concept.get('name').lower() for concept in result[
        'outputs'][0]['data']['concepts']]

    logger.info('Clarifai tags: %s', clarifai_tags)

    desired_tags_appear = set(clarifai_tags) & set(img_tags)
    banned_tags_appear = set(clarifai_tags) & set(img_tags_skip)

    if desired_tags_appear and not banned_tags_appear:
        logger.info('Clarifai test passed: the following tags are present: '
                    '%s and no banned tags appear', desired_tags_appear)
        return True, []
    else:
        logger.info('Clarifai test did not pass: the following tags '
                    'appear: %s and the following banned tags appear: %s ',
                    desired_tags_appear, banned_tags_appear)
        return False, []


def given_tags_in_result(search_tags, clarifai_tags, full_match=False):
    """Checks the clarifai tags if it contains one (or all) search tags """
    if full_match:
        return all([tag in clarifai_tags for tag in search_tags])
    else:
        return any((tag in clarifai_tags for tag in search_tags))


def get_imagelink(browser):
    """Gets the imagelink from the given webpage open in the browser"""
    return browser.find_element_by_xpath('//img[@class = "FFVAD"]') \
        .get_attribute('src')
