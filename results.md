| config | prompt | rounds | rounds/word | s/word | spec hits | widened | input tokens | tokens/word | reply |
|---|---|---|---|---|---|---|---|---|---|
| g=16 s=2 b=1 | Tell me about dogs. | 33 | 1.94 | 1.58 | 8/17 | 2 | 448k | 26.3k | Sure. They are animals. Dogs are loyal. And intelligent. Social. Great! |
| g=16 s=2 b=1 | How do I boil an egg? | 70 | 1.79 | 1.52 | 13/39 | 1 | 870k | 22.3k | First, bring a pot of water to boil. Place an egg in. Boil until done. Eight minutes. Perfect! Ice water for your egg. Then remove it! Your egg! Ready! |
| g=16 s=2 b=1 | Who are you? | 11 | 2.20 | 1.90 | 4/5 | 1 | 170k | 34.0k | I am an assistant. |
| g=16 s=2 b=1 | What is the capital of France? | 5 | 2.50 | 2.60 | 2/2 | 0 | 81k | 40.3k | Paris. |
| g=16 s=2 b=1 spec_min=0.4 | Tell me about dogs. | 57 | 1.84 | 1.51 | 8/31 | 0 | 323k | 10.4k | Dogs are animals. They are loyal. They also are intelligent. They often play. They love people. They can obey. They need care. They. |
| g=16 s=2 b=1 spec_min=0.4 | How do I boil an egg? | 51 | 1.89 | 1.57 | 8/27 | 1 | 369k | 13.7k | First bring a pot of water to boil. Place an egg in. Boil for six minutes. Let the cold run. Shell off. |
| g=16 s=2 b=1 spec_min=0.4 | Who are you? | 19 | 1.90 | 1.59 | 4/10 | 0 | 136k | 13.6k | I am an assistant. Can help with anything. |
| g=16 s=2 b=1 spec_min=0.4 | What is the capital of France? | 5 | 2.50 | 2.25 | 2/2 | 0 | 66k | 33.2k | Paris. |
| g=16 s=1 b=1 spec_min=0.0 | Tell me about dogs. | 84 | 1.68 | 1.41 | 23/50 | 3 | 757k | 15.1k | Certainly. The dog is an animal. The kingdom is the animal kingdom. Dogs have a tail. And they can fetch. Also more. They can play. Friendly. Loyal. Smart. Pet. Best friend. Are. Is. Are is. |
| g=16 s=1 b=1 spec_min=0.0 | How do I boil an egg? | 61 | 1.91 | 1.73 | 8/32 | 1 | 511k | 16.0k | First bring a pot of water to boil. Drop an egg. Boil five minutes. Take it. Let it. Until done. Cooked! Ready! Cold! |
| g=16 s=1 b=1 spec_min=0.0 | Who are you? | 18 | 1.80 | 1.53 | 5/10 | 0 | 157k | 15.7k | I am an assistant. Can help with anything. |
| g=16 s=1 b=1 spec_min=0.0 | What is the capital of France? | 6 | 3.00 | 2.50 | 1/2 | 0 | 66k | 33.2k | Paris. |
| g=16 s=2 b=1 spec_min=0.25 | Tell me about dogs. | 80 | 1.74 | 1.41 | 17/46 | 1 | 529k | 11.5k | Certainly. Dogs are animals. They are friendly. Some are intelligent. Loyal. They have tail. Their eyes are brown. Their nose. Their. Teeth. Are. Has. Have. Are has. Are sorry. Sorry. |
| g=16 s=2 b=1 spec_min=0.25 | How do I boil an egg? | 60 | 1.82 | 1.65 | 11/33 | 1 | 532k | 16.1k | First bring enough water to a boil. Drop an egg. Cover. Let it cook about nine minutes. Then put it under running water. Until cold. Okay. |
| g=16 s=2 b=1 spec_min=0.25 | Who are you? | 16 | 1.78 | 1.48 | 5/9 | 0 | 177k | 19.7k | I am an assistant. Can you tell? |
| g=16 s=2 b=1 spec_min=0.25 | What is the capital of France? | 5 | 2.50 | 2.45 | 2/2 | 0 | 66k | 33.2k | Paris. |
| g=16 s=2 b=1 window=8 | Tell me about dogs. | 33 | 1.65 | 1.36 | 10/20 | 0 | 259k | 12.9k | Dogs are animals. They are loyal. Friendly! They also have a tail. They can run. |
| g=16 s=2 b=1 window=8 | How do I boil an egg? | 74 | 1.80 | 1.55 | 15/41 | 2 | 695k | 16.9k | First bring a pot of water to boil. Drop an egg. Let it cook for a few minutes. Then transfer it into an ice water bowl. Let the egg cool for a minute. Then shell. |
| g=16 s=2 b=1 window=8 | Who are you? | 12 | 2.40 | 1.94 | 3/5 | 1 | 149k | 29.8k | I am an assistant. |
| g=16 s=2 b=1 window=8 | What is the capital of France? | 5 | 2.50 | 2.05 | 2/2 | 0 | 66k | 33.2k | Paris. |
| g=16 s=2 b=1 window=4 | Tell me about dogs. | 56 | 1.70 | 1.38 | 15/33 | 1 | 443k | 13.4k | Sure. I will talk about dogs: they are animals that have a tail. They have teeth. They also have eyes. They are loyal. They can run. |
| g=16 s=2 b=1 window=4 | How do I boil an egg? | 45 | 1.73 | 1.37 | 10/26 | 0 | 373k | 14.4k | First bring a pot of water. Then drop an egg into it and boil for minutes ten. Then you take out the egg. |
| g=16 s=2 b=1 window=4 | Who are you? | 8 | 1.60 | 1.26 | 5/5 | 0 | 103k | 20.7k | I am an assistant. |
| g=16 s=2 b=1 window=4 | What is the capital of France? | 5 | 2.50 | 2.15 | 2/2 | 0 | 67k | 33.3k | Paris. |
| g=16 s=2 b=1 skip=0.5 | Tell me about dogs. | 38 | 2.00 | 1.55 | 8/19 | 3 | 331k | 17.4k | Certainly. The dog is an animal. It is loyal. Also intelligent. They are friendly. |
| g=16 s=2 b=1 skip=0.5 | How do I boil an egg? | 41 | 1.78 | 1.41 | 7/23 | 1 | 387k | 16.8k | Bring water to boil. Place an egg in the pot and boil for about nine minutes. Take out and eat. |
| g=16 s=2 b=1 skip=0.5 | Who are you? | 17 | 1.89 | 1.54 | 5/9 | 1 | 187k | 20.8k | Am an assistant. How can you help? |
| g=16 s=2 b=1 skip=0.5 | What is the capital of France? | 5 | 2.50 | 2.15 | 2/2 | 0 | 67k | 33.3k | Paris. |
| g=16 s=2 b=1 skip=0.6 | Tell me about dogs. | 27 | 1.69 | 1.35 | 8/16 | 0/0 |191k | 11.9k | Dogs are animals. They are loyal. They can fetch. Friendly. Intelligent. |
| g=16 s=2 b=1 skip=0.6 | How do I boil an egg? | 36 | 1.80 | 1.39 | 5/20 | 0/2 |319k | 15.9k | First bring a pot water to boil. Drop an egg in. Count minutes. About seven minutes. |
| g=16 s=2 b=1 skip=0.6 | Who are you? | 22 | 1.69 | 1.37 | 6/13 | 0/1 |201k | 15.5k | Am an assistant. Can help you. How can I help? |
| g=16 s=2 b=1 skip=0.6 | What is the capital of France? | 5 | 2.50 | 2.10 | 2/2 | 0/0 |66k | 33.2k | Paris. |
| g=16 s=2 b=1 skip=0 | Tell me about dogs. | 65 | 1.97 | 1.64 | 12/33 | 4/0 |572k | 17.3k | Certainly. Dogs are animals. They have a tail. They also have eyes. They are friendly. Most dogs have teeth. They can run. They eat food. |
| g=16 s=2 b=1 skip=0 | How do I boil an egg? | 43 | 1.87 | 1.49 | 8/23 | 1/0 |397k | 17.3k | First bring enough cold water into a pot over heat. Then drop an egg. Let it boil for nine minutes. |
| g=16 s=2 b=1 skip=0 | Who are you? | 18 | 2.00 | 1.57 | 5/9 | 1/0 |173k | 19.3k | I am assistant. An assistant. Helpful. |
| g=16 s=2 b=1 skip=0 | What is the capital of France? | 5 | 2.50 | 1.90 | 2/2 | 0/0 |67k | 33.3k | Paris. |
| g=16 s=2 b=1  | Tell me about dogs. | 24 | 1.50 | 1.18 | 7/16 | 0/2 |199k | 12.4k | Certainly. They are animals. They can be friendly. Many dogs are loyal. |
| g=16 s=2 b=1  | How do I boil an egg? | 62 | 1.55 | 1.24 | 9/40 | 0/6 |538k | 13.5k | Here: how to boil an egg. You need: eggs. Then you put them in a pot of water and bring to the boil. Then turn down heat. Then cook for about nine minutes. |
| g=16 s=2 b=1  | Who are you? | 18 | 1.80 | 1.44 | 5/10 | 0/0 |201k | 20.1k | I am an assistant. How do you do. |
| g=16 s=2 b=1  | What is the capital of France? | 5 | 2.50 | 2.00 | 2/2 | 0/0 |74k | 36.9k | Paris. |
| g=16 s=2 b=1 skip=0 core=200 topic=150 | Tell me about dogs. | 35 | 1.84 | 1.39 | 6/19 | 0/0 |105k | 5.5k | Sure, dogs are friendly. They are loyal. They have a nose. They can fetch. |
| g=16 s=2 b=1 skip=0 core=200 topic=150 | How do I boil an egg? | 64 | 1.73 | 1.31 | 13/37 | 0/0 |186k | 5.0k | First put the eggs into water. Cold. Then bring the water to boil and time depends how long you want: soft or hard. For about six minutes. Then take them out. |
| g=16 s=2 b=1 skip=0 core=200 topic=150 | Who are you? | 42 | 2.47 | 1.87 | 5/17 | 5/0 |268k | 15.7k | I am an assistant. To help you. Can you? How do you do? |
| g=16 s=2 b=1 skip=0 core=200 topic=150 | What is the capital of France? | 6 | 3.00 | 2.60 | 1/2 | 0/0 |41k | 20.7k | Paris. |
| g=16 s=2 b=1 skip=0 core=250 topic=200 | Tell me about dogs. | 78 | 2.00 | 1.56 | 13/39 | 5/0 |386k | 9.9k | Sure. Dogs are animals. The best friends of man. More: they are loyal. They can protect. They have a nose. And teeth. The eyes. Tail / Ears. Smart. |
| g=16 s=2 b=1 skip=0 core=250 topic=200 | How do I boil an egg? | 54 | 1.80 | 1.39 | 9/30 | 0/0 |217k | 7.2k | First bring cold water to boil. Then place the egg into the water. Boil for about ten minutes. Take out and ice water for couple minutes. |
| g=16 s=2 b=1 skip=0 core=250 topic=200 | Who are you? | 10 | 2.00 | 1.54 | 3/5 | 0/0 |61k | 12.2k | I am an assistant. |
| g=16 s=2 b=1 skip=0 core=250 topic=200 | What is the capital of France? | 6 | 3.00 | 2.35 | 1/2 | 0/0 |44k | 21.8k | Paris. |
