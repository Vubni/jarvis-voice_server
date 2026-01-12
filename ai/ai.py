import asyncio
import time
from openai import AsyncOpenAI
from config import API_KEY

client = AsyncOpenAI(
    api_key=API_KEY
)

def calculate_cost(prompt_tokens, completion_tokens):
    INPUT_COST_PER_TOKEN = 0.4 / 1000000  # за 1 млн входных токенов
    OUTPUT_COST_PER_TOKEN = 1.6 / 1000000  # за 1 млн выходных токенов
    return (prompt_tokens * INPUT_COST_PER_TOKEN) + (completion_tokens * OUTPUT_COST_PER_TOKEN)

class Answer_ai:
    def __init__(self, messages=None, answer="", price=0.0, generation_time=0.0, tokens=0):
        self.messages = messages if messages is not None else []
        self.answer = answer
        self.price = price
        self.generation_time = generation_time
        self.tokens = tokens

class Ai:
    def __init__(self, system_prompt=None, model="gpt-5-mini", max_questions=None):
        self.model = model
        self.messages = []
        self.system_prompt = system_prompt
        self.price = 0
        self.max_questions = max_questions  # None — без ограничений

        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
            
    def edit_model(self, model:str):
        self.model = model

    def edit_system_prompt(self, system_prompt:str):
        self.system_prompt = system_prompt
        if self.messages:
            self.messages[0] = {"role": "system", "content": system_prompt}
        else:
            self.messages.insert(0, {"role": "system", "content": system_prompt})

    def add_question(self, content: str):
        system_message = self.messages[0] if self.messages and self.messages[0]["role"] == "system" else None
        
        self.messages.append({"role": "user", "content": content})
        self._enforce_max_questions(system_message)

    def _enforce_max_questions(self, system_message):
        user_messages = [msg for msg in self.messages if msg["role"] == "user"]
        
        if self.max_questions is not None and len(user_messages) > self.max_questions:
            first_user_index = next(i for i, msg in enumerate(self.messages) if msg["role"] == "user")
            
            del self.messages[first_user_index:first_user_index + 2]
            self._enforce_max_questions(system_message)

    async def question(self, content=None, memory=True):
        if content:
            user_message = {"role": "user", "content": content}

            if memory:
                system_message = self.messages[0] if self.messages and self.messages[0]["role"] == "system" else None
                self.messages.append(user_message)
                self._enforce_max_questions(system_message)
                current_messages = self.messages
            else:
                if self.system_prompt:
                    current_messages = [
                        {"role": "system", "content": self.system_prompt},
                        user_message
                    ]
                else:
                    current_messages = [user_message]
        else:
            current_messages = self.messages

        start_time = time.time()
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=current_messages
            )
        except Exception as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        end_time = time.time()

        answer_content = response.choices[0].message.content
        usage = response.usage
        cost = calculate_cost(usage.prompt_tokens, usage.completion_tokens)
        generation_time = end_time - start_time

        if memory:
            self.messages.append({"role": "assistant", "content": answer_content})
            self._enforce_max_questions(self.messages[0] if self.messages and self.messages[0]["role"] == "system" else None)
            answer_messages = self.messages.copy()
        else:
            answer_messages = current_messages.copy()
            answer_messages.append({"role": "assistant", "content": answer_content})

        self.price += cost
        return Answer_ai(
            messages=answer_messages,
            answer=answer_content,
            price=cost,
            generation_time=generation_time,
            tokens = usage.prompt_tokens + usage.completion_tokens
        )

    def clear_messages(self):
        self.messages = []
        return True

# Пример использования
async def main():
    ai = Ai(system_prompt="You are a helpful assistant")
    
    try:
        # Первый вопрос
        result1 = await ai.question("Объясни теорию относительности Эйнштейна")
        print(f"Ответ 1: {result1.answer}")
        print(f"Стоимость: ${result1.price:.5f}")
        print(f"Время генерации: {result1.generation_time:.2f} сек")
        
        # Второй вопрос с использованием памяти
        result2 = await ai.question("Как это связано с GPS?")
        print(f"\nОтвет 2: {result2.answer}")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())