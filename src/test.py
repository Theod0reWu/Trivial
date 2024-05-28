from clues import Clue

def parse_content(content):
	lines = content.split("\n")
	clues = []
	
	q_at = -1
	x = 0
	while (x < len(lines)):
		if (lines[x][:9] == "Question:"):
			q_at = x
		if (lines[x][:7] == "Answer:" and q_at != -1):
			clues.append(Clue(lines[q_at][9:], lines[x][7:]))
			q_at = -1
		x+=1
	return clues

clues = parse_content("""Question: A young boy with a lightning-shaped scar who is unknowingly a wizard on a quest to defeat an evil wizard.
Answer: Harry Potter

Question: A group of friends who go on an adventure to find a lost city of gold.
Answer: The Goonies

Question: A young woman who is chosen to be the leader of a rebellion against an oppressive government.
Answer: Katniss Everdeen

Question: A group of soldiers who are sent on a mission to rescue hostages from a terrorist organization.
Answer: The Avengers

Question: A woman who is falsely accused of murder and must clear her name while trying to stay one step ahead of the police.
Answer: The Fugitive""")

for i in clues:
	print(i.clue)
	print(i.answer)