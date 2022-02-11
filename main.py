import akinator
from keyboard import AKI_LANG_BUTTON, AKI_PLAY_KEYBOARD, AKI_WIN_BUTTON, CHILDMODE_BUTTON
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from config import BOT_TOKEN
from db_map import main, adduser, getchildmode, getlanguage, updatelanguage, updatechildmode
from strings import AKI_FIRST_QUESTION, AKI_LANG_CODE, AKI_LANG_MSG, CHILDMODE_MSG, START_MSG

main()

def aki_start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    user_name = update.effective_user.username
    #Adding user to the database.
    adduser(user_id, first_name, last_name, user_name)
    update.message.reply_text(START_MSG.format(first_name),
                              parse_mode=ParseMode.HTML)

def aki_play_cmd_handler(update: Update, context: CallbackContext) -> None:
    #/play command.
    aki = akinator.Akinator()
    user_id = update.effective_user.id
    msg = update.message.reply_text(
        text = "Wait..."
    )
    q = aki.start_game(language = getlanguage(user_id), child_mode = getchildmode(user_id))
    context.user_data[f"aki_{user_id}"] = aki
    context.user_data[f"q_{user_id}"] = q
    context.user_data[f"ques_{user_id}"] = 1
    msg.edit_text(text = q, reply_markup=AKI_PLAY_KEYBOARD)


def aki_play_callback_handler(update: Update, context:CallbackContext) -> None:
    user_id = update.effective_user.id
    aki = context.user_data[f"aki_{user_id}"]
    q = context.user_data[f"q_{user_id}"]
    query = update.callback_query
    a = query.data.split('_')[-1]
    if a == '5':
        try:
            q = aki.back()
        except akinator.exceptions.CantGoBackAnyFurther:
            query.answer(text=AKI_FIRST_QUESTION, show_alert=True)
            return
    else:
        q = aki.answer(a)
    query.answer()
    if aki.progression < 80:
        query.message.edit_text(
            text = q, reply_markup = AKI_PLAY_KEYBOARD
        )
        context.user_data[f"aki_{user_id}"] = aki
        context.user_data[f"q_{user_id}"] = q
    else:
        aki.win()
        aki = aki.first_guess
        query.message.edit_text(text = f"It's {aki['name']} ({aki['description']})! Was I correct?",
                                reply_markup=AKI_WIN_BUTTON
                                )
        del_data(context, user_id)


def aki_win(update: Update, context: CallbackContext):
    query = update.callback_query
    ans = query.data.split('_')[-1]
    if ans =='y':
        query.message.edit_text(text ="Yeah, I win. If you want to play again: type /play", reply_markup=None)
    else:
        query.message.edit_text(text ="I'm lose :(. If you want to play again type /play", reply_markup=None)


def aki_set_lang(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    lang_code = query.data.split('_')[-1]
    user_id = update.effective_user.id
    updatelanguage(user_id, lang_code)
    query.edit_message_text(f"Language Successfully changed to {AKI_LANG_CODE[lang_code]} !")


def aki_lang(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    update.message.reply_text(AKI_LANG_MSG.format(
        AKI_LANG_CODE[getlanguage(user_id)]), parse_mode=ParseMode.HTML,reply_markup=AKI_LANG_BUTTON
    )


def aki_childmode(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    status = "enabled" if getchildmode(user_id) else "disabled"
    update.message.reply_text(
        text=CHILDMODE_MSG.format(status), parse_mode=ParseMode.HTML, reply_markup=CHILDMODE_BUTTON
    )


def aki_set_child_mode(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    query = update.callback_query
    to_set = int(query.data.split('_')[-1])
    updatechildmode(user_id, to_set)
    query.edit_message_text(f"Child mode is {'enabled' if to_set else 'disabled'} Successfully!")


def del_data(context:CallbackContext, user_id: int):
    del context.user_data[f"aki_{user_id}"]
    del context.user_data[f"q_{user_id}"]


def main():
    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', aki_start, run_async=True))
    dp.add_handler(CommandHandler('play', aki_play_cmd_handler, run_async=True))
    dp.add_handler(CommandHandler('language', aki_lang, run_async=True))
    dp.add_handler(CommandHandler('childmode', aki_childmode, run_async=True))

    dp.add_handler(CallbackQueryHandler(aki_set_lang, pattern=r"aki_set_lang_", run_async=True))
    dp.add_handler(CallbackQueryHandler(aki_set_child_mode, pattern=r"c_mode_", run_async=True))
    dp.add_handler(CallbackQueryHandler(aki_play_callback_handler, pattern=r"aki_play_", run_async=True))
    dp.add_handler(CallbackQueryHandler(aki_win, pattern=r"aki_win_", run_async=True))

    '''
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=BOT_TOKEN)
    updater.bot.setWebhook('https://msai-bot.herokuapp.com/' + BOT_TOKEN)
    '''
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
