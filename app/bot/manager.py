import typing

from app.store.tg_api.models import Update

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotStates
    from app.bot.states.state_manager import FSM
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.router = app.bot.router
        self.fsm: "FSM" = app.bot.fsm
        self.middleware = app.bot.middleware
        self.handler = self.app.bot.handlers
        self.states: "BotStates" = self.app.bot.states

        self._register_routes()

    def _register_routes(self):
        #message routers
        self.router.register("/start")(
            self.handler.command.start_command
        )
        self.router.register("/start@Test_20053_bot")(
            self.handler.command.start_command
        )
        self.router.register("/create_game", self.states.creation_game)(
            self.handler.command.creation_game
        )
        self.router.register(None, self.states.question_active)(
            self.handler.command.creation_game
        )
        self.router.register("/answer", self.states.check_answer)(
            lambda message: self.middleware.auth.answering_only_middleware(
                self.handler.command.answer_command, message=message
            )
        )
        self.router.register("/get", self.states.check_answer)(
            lambda message: self.middleware.auth.captain_only_middleware(
                self.handler.command.get_answer, message=message
            )
        )

        #callback routers
        self.router.callback_register("join", self.states.add_users)(
            self.handler.callback.add_user
        )
        self.router.callback_register("select", self.states.select_capitan)(
            self.handler.callback.select_capitan
        )
        self.router.callback_register("start", self.states.start_game)(
            lambda callback: self.middleware.auth.captain_only_middleware(
                self.handler.callback.start_game, callback=callback
            )
        )
        self.router.callback_register("next", self.states.finish)(
            lambda callback: self.middleware.auth.captain_only_middleware(
                self.handler.callback.start_game_with_same_team, callback=callback
            )
        )
        self.router.callback_register("quite", self.states.finish)(
            lambda callback: self.middleware.auth.player_only_middleware(
                self.handler.callback.quite_game, callback=callback
            )
        )
        self.router.callback_register("user", self.states.check_answer)(
            lambda callback: self.middleware.auth.captain_only_middleware(
                self.handler.callback.answering_player, callback=callback
            )
        )


    async def handle_updates(self, updates: list[Update]):
        for index, update in enumerate(updates):
            if update.type_query == "message" and update.message.text:
                command = update.message.text.strip().split()[0]
                chat_id = update.message.chat.id
                args = (update.message,)
            elif update.type_query == "callback_query":
                command = update.callback_query.data.split('_')[0]
                chat_id = update.callback_query.message.chat.id
                args = (update.callback_query,)
            else:
                continue

            current_state = self.fsm.get_state(chat_id)

            if command and update.type_query:
                await self.router.handle(
                    update.type_query, command, current_state, *args
                )


def setup_manager(app: "Application"):
    app.bot.manager = BotManager(app)
