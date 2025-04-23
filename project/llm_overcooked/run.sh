python run_game.py \
  --model_name gpt-4o \
  --num_agents 2 \
  --level level_0 \
  --structured > level_0_2_gpt-4o_struct.txt

python run_game.py \
  --model_name gpt-4o \
  --num_agents 2 \
  --level level_0 > level_0_2_gpt-4o_nl.txt

python run_game.py \
  --model_name gpt-4o \
  --num_agents 3 \
  --level level_3 \
  --structured > level_3_3_gpt-4o_struct.txt

python run_game.py \
  --model_name gpt-4o \
  --num_agents 3 \
  --level level_3 > level_3_3_gpt-4o_nl.txt