from json import load
from re import sub as regex_replace
from hgtk.letter import decompose
from hgtk.checker import has_batchim
from tqdm import tqdm

print("loading...")

counter_total: int = 0  # 총 글자 수
counter_letter: int = 0  # 받침이 있는 글자의 수
counter_same: int = 0  # 초성과 종성이 같은 글자의 수
counter_reverse: int = 0  # 초성과 종성이 역가나다순인 글자의 수

# 한글 자음
HANGUL_CONSONANTS: list[str] = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ',
                                'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# 각자병서: ㄱ이 ㄲ보다 먼저이지만, 준세벌식 키보드에서는 초성에 된소리가 오는 것이 원래의 순서이기에 초성에 한해 처리해 주어야 함.
GEMINATION_CLUSTERS: dict[str, str] = {"ㄲ": "ㄱ", "ㄸ": "ㄷ", "ㅃ": "ㅂ", "ㅆ": "ㅅ", "ㅉ": "ㅈ"}
# 합용병서자가 아닌 병서자라는 의미로 사용됨
CONSONANT_CLUSTERS: dict[str, str] = {"ㄺ": "ㄱ", "ㄻ": "ㅁ", "ㄼ": "ㅂ", "ㄽ": "ㅅ",
                                 "ㄾ": "ㅌ", "ㄿ": "ㅍ", "ㅀ": "ㅎ", "ㄳ": "ㅅ",
                                 "ㄵ": "ㅈ", "ㄶ": "ㅎ", "ㅄ": "ㅂ"}

def cut_out(target_list: list, index: int) -> list:
    """주어진 리스트에서 한 요소를 제외한 요소를 리턴합니다

    Args:
        target_list (list[Any]): 대상 리스트
        index (int): 삭제할 요소의 index

    Returns:
        list[Any]: 요소가 삭제된 리스트
    """
    # if len(target_list)-1 < index: return target_list
    return target_list[:index] + target_list[index+1:]

datas =  open('./data/ko_dataset_2.json', 'r', encoding="UTF8")
for data in tqdm(load(datas)):  # CONVERSATION_DATA에 대화 데이터 추가
    conversation_data: str = ''
    for conversation in data["conversations"]:
        conversation_data += conversation["value"]
    
    conversation_data = regex_replace('[^각-힣]', '', conversation_data)

    for letter in conversation_data:
        counter_total += 1
        # 받침 없을 시 다음 루프로
        if not has_batchim(letter):
            continue

        # 받침이 존재하는 글자에 한해서 실행
        consonants:list[str] = cut_out(list(decompose(letter)), 1)  # 초성과 종성만 변수로 로드

        # 초성자가 각자병서자일 시 병서자가 아닌 자음으로 교체
        consonants[0] = GEMINATION_CLUSTERS.get(consonants[0], consonants[0])

        # ㄲ, ㅆ 받침 예외처리 (각각 키가 할당되어 있기에 순서의 영향을 받지 않음.)
        if (consonants[1] == "ㄲ" or
            consonants[1] == "ㅆ"):
            continue

        # 종성자가 합용병서자일 시 병서자가 아닌 자음으로 교체.
        # 준세벌식 키보드에서 종성자는 초성과 종성이 동일한 경우를 제외하고 'ㄲ'이나 'ㅆ'이 아닌 각자병서자일 수 없음.
        consonants[1] = CONSONANT_CLUSTERS.get(consonants[1], consonants[1])

        # 카운트
        counter_letter += 1
        if consonants != sorted(consonants):
            counter_reverse += 1
        elif len(set(consonants)) == 1:
            counter_same += 1

datas.close()
print(f"Complete.\nThe length of data is {counter_total}")

# 분석 완료 후 출력
print("\n\n---Final Result---")
print(f"letter : {counter_letter}")
print(f"same : {counter_same}")
print(f"reversed : {counter_reverse}")
print(f"unreversed : {counter_letter - counter_reverse - counter_same}")
