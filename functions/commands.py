from ai.ai import Ai
from ai.prompts import PROMPT_COMMAND_ANALYZE, PROMPT_CLASSIFICATION, PROMPT_DIALOGS
from database.database import Database
import json, re

ai = {}
paths_progprams = {}
user_prompts = {}

def replace_tokens(text, token_dict):
    """
    Заменяет все вхождения &ключ& в text на значения из token_dict.
    Если ключ не найден, оставляет подстроку без изменений.
    """
    pattern = r'&([^&]+)&'  # Ищет подстроки между &...&
    return re.sub(
        pattern,
        lambda m: token_dict.get(m.group(1)),  # Пытаемся извлечь значение
        text)

def create_ai(user_id:int, path_program:dict):
    paths_progprams[user_id] = path_program
    keys_str = "\n".join(str(key) for key in path_program)
    prompt = PROMPT_COMMAND_ANALYZE.replace("&PathProgram&", keys_str)
    user_prompts[user_id] = prompt
    ai[user_id] = Ai(PROMPT_CLASSIFICATION, max_questions=5)
    
    
    
async def action_generate(db:Database, user_id:int, input_phrase:str, save_cache:bool):
    try:
        ai[user_id].edit_system_prompt(PROMPT_COMMAND_ANALYZE)
        
        result = await ai[user_id].question(input_phrase)
        result.answer = json.loads(result.answer)
        if "cached" in result.answer and save_cache:
            await db.execute("INSERT INTO commands (user_id, phrase, command, answer) VALUES ($1, $2, $3, $4)", (user_id, input_phrase, result.answer["action"], result.answer["answer"]))
            del result.answer["cached"]
        if "action" in result.answer:
            result.answer["action"] = replace_tokens(result.answer["action"], paths_progprams[user_id])
        else:
            result.answer["action"] = ""
        if not "answer" in result.answer:
            result.answer["answer"] = ""
    except:
        return False
    return result.answer

async def answer_generate(db:Database, user_id:int, input_phrase:str):
    try:
        ai[user_id].edit_system_prompt(PROMPT_DIALOGS)
        ai[user_id].edit_model("gpt-5-nano")
        
        result = await ai[user_id].question(input_phrase)
    except:
        return False
    return {"answer": result.answer, "action": ""}




async def command_processing(user_id: int, text_ru: str, text_en: str, save_cache: bool):
    """
    Проверяет наличие похожей фразы в БД для указанного пользователя
    
    Args:
        pool: Пул подключений к БД
        user_id: ID пользователя
        input_phrase: Проверяемая фраза
    
    Returns:
        str: Команда из БД, если фраза найдена, иначе None
    """
    if user_id not in ai:
        return
    
    async with Database() as db:
        # SQL-запрос с проверкой схожести
        query = """
            SELECT answer, command FROM commands
            WHERE user_id = $1 
            AND similarity(phrase, $2) >= 0.9
        """
        result = await db.execute(query, (user_id, text_ru))
        
        if result:
            return {"answer": result["answer"], "action": result['command']}
        else:
            ai[user_id].edit_model("gpt-5-mini")
            ai[user_id].edit_system_prompt(PROMPT_CLASSIFICATION)
            # Вызов функции execute при отсутствии совпадений
            result = await ai[user_id].question(text_ru)
            try:
                result = json.loads(result.answer)
                if result["type"] == "action":
                    return await action_generate(db, user_id, text_ru, save_cache)
                elif result["type"] == "answer":
                    return await answer_generate(db, user_id, text_ru)
                else:
                    return {"answer": "", "action": ""}
            except:
                return False
        
        
async def clear_cache(user_id):
    async with Database() as db:
        await db.execute("DELETE FROM commands WHERE user_id=$1", (user_id,))