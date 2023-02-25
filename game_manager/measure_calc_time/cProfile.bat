python -m cProfile -o game_manager.prof game_manager/game_manager.py --game_time 10 ^
    --seed 0 --obstacle_height 0 --obstacle_probability 0 --drop_interval 1 --mode default ^
    --user_name window_sample --resultlogjson result.json --train_yaml config/default.yaml ^
    --predict_weight outputs/latest/best_weight.pt --ShapeListMax 6 --BlockNumMax -1 ^
    --art_config_filepath default.json