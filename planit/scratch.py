current_word = topicInformation.objects.filter(linked_text=word).first()
descriptions = current_word.description.all()
line_wording = []
for line in descriptions:
    desc = line.Description
    line_wording.append(desc)

line_wording = '; '.join(line_wording)
sim_score = check_topic_relevance(line_wording, lesson_id)
results = current_word.item, line_wording, sim_score, current_word.id
word_counts = word_counts + 1

if results not in final_terms:
    final_terms.append(results)