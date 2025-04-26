import asyncio
import typing

from app.store.game.accessor import GameAccessor
from app.store.tg_api.models import Chat, Message, Update, User

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotState
    from app.bot.states.state_manager import FSM
    from app.web.app import Application

def fake_message(chat_id: int) -> Message:
    return Message(
        chat=Chat(id=chat_id),
        message_id=0,
        from_user=User(id=0, first_name="bot", username="bot"),
        date=0,
        text="",
    )


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.router = app.bot.router
        self.fsm: "FSM" = app.bot.fsm
        self.middleware = app.bot.middleware
        self.handler = self.app.bot.handlers
        self.states: "BotState" = self.app.bot.states
        self.active_tasks =  self.app.bot.active_tasks
        self.db: "GameAccessor" = app.store.game

        app.add_event_handler("startup", self.connect)
        app.add_event_handler("shutdown", self.disconnect)

    async def connect(self):
        self._register_routes()
        await self._resume_active_states()

    async def disconnect(self):
        for chat_id, tasks in list(self.active_tasks.items()):
            if tasks:
                for task in tasks:
                    if not task.done():
                        try:
                            task.cancel()
                            await asyncio.wait_for(task, timeout=5) 
                        except (asyncio.CancelledError, asyncio.TimeoutError, Exception ):
                            pass

        self.active_tasks.clear()

        if hasattr(self.app.bot, "session"):
            await self.app.bot.session.close()

    async def _resume_active_states(self):
        
        chats = await self.db.get_all_chats()
        if not chats:
            return
        for chat in chats:
            self.app.log.info(chat.bot_state)
            chat_id = chat.id
            state = chat.bot_state

            if chat_id in self.app.bot.active_tasks:
                continue  
            await self.router.on_startup_handle(state, message=fake_message(chat_id))

    def _register_routes(self):
        #startup routers
        self.router.startup_register(self.states.check_answer)(
            self.handler.game.process_answer
        )
        self.router.startup_register(self.states.round_results)(
            self.handler.game.round_results
        )
        self.router.startup_register(self.states.finish)(
            self.handler.game.finish_game
        )
        self.router.startup_register(self.states.question_active)(
            self.handler.game.start_round
        )
        self.router.startup_register(self.states.select_answering)(
            self.handler.game.process_answer
        )

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
        self.router.register("/create_game@Test_20053_bot", self.states.creation_game)(
            self.handler.command.creation_game
        )
        self.router.register(command=None, state=self.states.check_answer)(
            lambda message: self.middleware.auth.answering_only_middleware(
                self.handler.command.answer_command, message=message
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
        self.router.callback_register("next", self.states.lobbi)(
            lambda callback: self.middleware.auth.player_only_middleware(
                self.handler.callback.start_game_with_same_team, callback=callback
            )
        )
        self.router.callback_register("quite", self.states.add_users)(
            lambda callback: self.middleware.auth.player_only_middleware(
                self.handler.callback.quite_game, callback=callback
            )
        )
        self.router.callback_register("userquite", self.states.lobbi)(
            lambda callback: self.middleware.auth.player_only_middleware(
                self.handler.callback.userquite_game, callback=callback
            )
        )
        
        self.router.callback_register("get", self.states.select_answering)(
            lambda callback: self.middleware.auth.captain_only_middleware(
                self.handler.callback.get_answer, callback=callback
            )
        )
        self.router.callback_register("user", self.states.select_answering)(
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

            current_state = await self.fsm.get_state(chat_id)
            if not current_state:
                current_state = self.states.none
            self.app.log.info(current_state)
            if command and update.type_query:
                await self.router.handle(
                    update.type_query, 
                    command, 
                    current_state, 
                    *args
                )


def setup_manager(app: "Application"):
    app.bot.manager = BotManager(app)
