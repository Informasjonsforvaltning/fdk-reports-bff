import asyncio


def create_dataset_report(orgpath, theme, theme_profile):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    asyncio.set_event_loop(loop)
    return None
