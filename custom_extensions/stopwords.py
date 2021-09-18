stopwords_list = ['FDA', 'APE', 'MOON', 'HOLD', 'MERGE', 'ADS', 'FOMO', 'OTC', 'IMO', 'TLDR', 'SHIT', 'ETF', 'BOOM',
                  'THANK', 'PPP', 'REIT', 'HOT', 'MAYBE', 'AKA', 'CBS', 'SEC', 'OVER', 'ROPE', 'MOON', 'SSR',
                  'HOLD', 'SELL', 'BUY', 'COVID', 'GROUP', 'MONDA', 'USA', 'YOLO', 'MUSK', 'STONK', 'ELON', 'CAD', 'WIN',
                  'BETS', 'BET', 'STONK', 'DFV', 'ELON', 'ATH', 'AIM', 'IPO', 'EDIT', 'EDITED', 'NYC', 'NYSE', 'APES',
                  'DROP', 'CFO', 'EST', 'CSM', 'EPS', 'TERM', 'ITA', 'CEO', 'USD', 'WSB', 'PLC', 'UGL', 'CAGR', 'CASH',
                  'HAND', 'HANDS', 'GAMMA', 'MONEY', 'DD', 'TIME', 'BOYS', 'SOLD', 'CRAZY', 'STOCK', 'PRICE', 'WEEK',
                  'DAY', 'MONTH', 'SET', 'WEEKS', 'DAYS', 'SET', 'LOT', 'GAINS', 'HEDGE', 'FUND', 'FUNDS', 'POST',
                  'ROOF', 'CLOSE', 'RED', 'DATA', 'LEVEL', 'BASED', 'COST', 'FEEL', 'TAKES', 'FLOAT', 'TOTAL', 'TIMES',
                  'HAT', 'CHAIN', 'ITM', 'WAIT', 'RISE', 'SOLID', 'FUN', 'HEARD', 'LOTS', 'FUCK', 'FUD', 'SUB',
                  'RSI', 'DM', 'ING', 'POWW', 'TALK', 'PM', 'LEAP', 'LEAPS', 'GAME', 'GAY', 'OK',
                  'WITH', 'WON', 'ARE', 'DID', 'HERS', 'ON', 'ISNT', 'HE', 'YOUD', 'AM', 'WHICH', 'THESE', 'UNDER',
                  'HAS', 'OTHER', 'LL', 'YOULL', 'DOES', 'RE', 'WHEN', 'ABOUT', 'YOUVE', 'THEY', 'FEW', 'YOU', 'Y',
                  'THEM', 'BUT', 'MA', 'WILL', 'WHILE', 'HOW', 'HAD', 'WHERE', 'NOR', 'WERE', 'HASN', 'OURS', 'SHE',
                  'THEN', 'NOW', 'OF', 'HADNT', 'WAS', 'WHO', 'MUSTN', 'OR', 'AS', 'AIN', 'MORE', 'THEIR', 'DONT',
                  'ARENT', 'SHAN', 'THIS', 'T', 'OVER', 'MY', 'DIDN', 'NEEDN', 'OUR', 'ANY', 'ALL', 'AREN', 'DO',
                  'FROM', 'OWN', 'HIM', 'YOUR', 'BEEN', 'NOT', 'VERY', 'NO', 'INTO', 'IT', 'JUST', 'ITS', 'MOST',
                  'ONCE', 'ISN', 'DOWN', 'TO', 'OUT', 'AGAIN', 'HADN', 'SO', 'HIS', 'M', 'TOO', 'S', 'SHES', 'WASNT',
                  'DIDNT', 'IN', 'HASNT', 'AN', 'BEING', 'WHAT', 'THERE', 'THOSE', 'WEREN', 'SOME', 'IF', 'DOESN',
                  'HAVEN', 'BOTH', 'VE', 'THAN', 'AFTER', 'CAN', 'THAT', 'THE', 'HERE', 'AND', 'WONT', 'DON', 'IS',
                  'UP', 'WHY', 'SUCH', 'BY', 'EACH', 'ME', 'WHOM', 'SAME', 'YOURS', 'WASN', 'WE', 'YOURE', 'AT',
                  'OFF', 'ONLY', 'I', 'DOING', 'A', 'BE', 'SHANT', 'D', 'HER', 'HAVE', 'ABOVE', 'FOR', 'O', 'BELOW',
                  'UNTIL', 'SEE', 'GO', 'BIG', 'NEXT', 'WELL', 'EVER', 'LOSE', 'LOSS', 'LOST', 'GAIN', 'OPEN', 'FREE',
                  'LOW', 'RH', 'INFO', 'MIC', 'EXP', 'ONE', 'TWO', 'AMP', 'MAN', 'RIDE', 'KIDS', 'NEW', 'GOOD', 'BEST',
                  'REAL', 'HOPE', 'HUGE', 'LOVE', 'WORK', 'PLAY', 'STAY', 'SAN', 'GT', 'TECH', 'PLAN', 'ROLL', 'NINE',
                  'CARE', 'ICE', 'SEED', 'TELL', 'APR', 'MAY', 'JUN', 'JULY', 'JAN', 'FEB', 'MAR', 'AUG', 'SEP', 'OCT',
                  'NOV', 'DEC', 'CAP', 'ELSE', 'TURN', 'FORM', 'NICE', 'IRS', 'CPA', 'GROW', 'B', 'SUM', 'MIND', 'LIFE',
                  'ID', 'FLOW', 'COLD', 'OI', 'CUM', 'ASS', 'CAR', 'ROAD', 'SAVE', 'LAZY', 'SAFE', 'TRUE', 'DD', 'AGO',
                  'HI', 'MAR', 'BLUE', 'EYE', 'X', 'EAT', 'AIR', 'BIT', 'GOLD', 'EV', 'RUN', 'HES', 'RARE', 'SEVEN'
                  'ALEX', 'SAP', 'BC', 'LIVE', 'MET', 'MAIN', 'U', 'HOME', 'LOAN', 'SIX', 'FIVE', 'FOUR', 'EIGHT',
                  'THREE', 'CARS', 'MC', 'VS', 'PS', 'JOBS', 'BIDEN', 'FUSE', 'DUDE', 'L', 'PAYS', 'HEAR', 'CO',
                  'LOOP', 'KEY', 'PDT', 'SITE', 'MIN', 'CAT', 'MAX', 'FDS', 'TEN', 'BILL', 'W', 'ONTO', 'FAST', 'TEN'
                  'FOLD', 'THO', 'POOL', 'WGO', 'PEAK', 'SHIP', 'LEG', 'RACE', 'LAWS', 'DASH', 'FAT', 'PUMP', 'DUMP',
                  'JOB', 'PPL', 'FT', 'AGE', 'GOGO', 'FROG', 'TD', 'CAKE', 'TEAM', 'RIG', 'FAM', 'EYES', 'TRIP',
                  'DARE', 'PLUS', 'IQ', 'DDS', 'ROCK', 'LAND', 'JACK', 'SI', 'GLAD', 'WOW', 'RC', 'CTO', 'PT', 'BOB',
                  'TV', 'IP', 'BRO', 'BAND', 'PAY']
