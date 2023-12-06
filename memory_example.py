import argparse
from uac.memory.interface import MemoryInterface
from uac.memory.faiss import FAISS
from uac.provider import OpenAIProvider

def main(args):

    embedding_provider = OpenAIProvider()
    embedding_provider.init_provider(args.providerConfig)
    vectorstore = FAISS(embedding_provider = embedding_provider, memory_path = '')
    memory = MemoryInterface(memory_path = '', 
                             vectorstores = {"basic_memory":{"description":vectorstore},'decision_making':{},'success_detection':{}}, 
                             embedding_provider = embedding_provider) 
    
    for step in range(10):
        key = step*10+5
        data = {key:{"instruction":"This is an instruction",
                     "screenshot":"This is a screenshot",
                     "timestep": step,
                     "description": "This the number" + str(step),
                     "inventory": "This is an inventory"}}
        memory.add_experiences(data)
    sim_mem = memory.get_similar_experiences(data = 'This the number 9',top_k = 3)
    print(sim_mem)
    '''
    [{'instruction': 'This is an instruction', 'screenshot': 'This is a screenshot', 'timestep': 9, 'description': 'This the number9', 'inventory': 'This is an inventory'}, {'instruction': 'This is an instruction', 'screenshot': 'This is a screenshot', 'timestep': 8, 'description': 'This the number8', 'inventory': 'This is an inventory'}, {'instruction': 'This is an instruction', 'screenshot': 'This is a screenshot', 'timestep': 7, 'description': 'This 
the number7', 'inventory': 'This is an inventory'}]
    '''
    rec_mem = memory.get_recent_experiences(recent_k = 3)
    print(rec_mem)
    '''
    [{'instruction': 'This is an instruction', 'screenshot': 'This is a screenshot', 'timestep': 7, 'description': 'This the number7', 'inventory': 'This is an inventory'}, {'instruction': 'This is an instruction', 'screenshot': 'This is a screenshot', 'timestep': 8, 'description': 'This the number8', 'inventory': 'This is an inventory'}, {'instruction': 'This is an instruction', 'screenshot': 'This is a screenshot', 'timestep': 9, 'description': 'This 
the number9', 'inventory': 'This is an inventory'}]
    '''


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--providerConfig",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    main(args)