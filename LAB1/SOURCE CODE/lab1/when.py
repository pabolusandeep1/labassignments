__author__ = 'Anirudh'

import WM
import NET
import nltk
nltk.data.path.append("/home/anirudhn/nltk_data")

# The selection of answer is based on the sentence which gets the maximum total score across the four conditions ##

# But generally answers to "when" questions almost always involves a time expression, so sentences that do not contain a time
# expression are only considered in special cases

def answering_when(cleansedQuestion,stop_words_free_question,complete_sentence_list,sentence_list,dateline,month_list,time_list):

    # Declaring globals to be used in this function

    candidate_list=[]
    sent_score_list=[]


    stanford_stop_words_list=['a','an','and','are','as','at','be','buy','for','from',
                          'has','he','in','is','it','its','of','on','that','the',
                          'to','was','were','will','with']



    time_nos=['one','two','three','four','five','six','seven','eight','nine','ten',
              'twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety','hundred',
              'thousand','million','billion','trillion']


    temp_q=cleansedQuestion
    temp_q=temp_q.replace('"','')
    temp_q=temp_q.replace("'",'"')
    temp_q=temp_q.replace('?','')

    #print 'Question is :',temp_q

    #print 'Month list is :',month_list
    #print 'Time list is :',time_list
    # 1. Check if the sentence contains "TIME" expression


    #print 'Time list is :',time_list
    for i in range(0,len(sentence_list)):
        score=0
        #print 'Sentence is :',complete_sentence_list[i]
        if time_list[i] != [] or month_list[i]!= []: # Sentence contains a time expression

            # Now compute the wordmatch score
            score = score + 4 + WM.stemWordMatch(cleansedQuestion,sentence_list[i])

        # 2. Check if the Question contains "the last" and sentence contains any of "first,last,since,ago", then score+= slam_dunk

        temp=cleansedQuestion.split()
        for m in range(0, len(temp)-1):
            if temp[m].lower()=='the' and temp[m+1].lower()=='last':
                for sent in  sentence_list[i].split():
                    if sent in ['first','last','since','ago']:
                        score = score +20


            # 3. If the question contains {start,begin} and sentence contains {start,begin,since,year}
        for word in cleansedQuestion.split():
            if word.lower() in ['start','begin']:
                for sent in  sentence_list[i].split():
                    if sent in ['start','begin','since','year']:
                        score = score +20

        sent_score_list.append(score)


        #4. Verb match ??


    #print 'Sent score list is :', sent_score_list


    ##################### COMPUTING THE DATE LINE SCORE FOR THE QUESTION #####################

    # For when and where questions the answer to the question could also be from the timeline of the story

    dateline_score=0
    temp_list=cleansedQuestion.split()
    for i in range(0, len(temp_list)):
        # 1. If question contains "happen", it is a good clue that timeline could be answer
        if temp_list[i].lower()=='happen':
            dateline_score= dateline_score+4

        # 2. If question contains "take place", it is a good clue that timeline could be answer
        if i != len(temp_list)-1 and temp_list[i].lower()=='take' and temp_list[i+1].lower()=='place':
            dateline_score=dateline_score+4

        # 3. If question contains "this", it is slam_dunk that timeline could be answer
        if temp_list[i].lower()=='this':
            dateline_score= dateline_score+20

        # 4. If question contains "story", it is slam_dunk that timeline could be answer

        if temp_list[i].lower()=='story':
            dateline_score= dateline_score+20

    #print 'Date line score for the question is :',dateline_score


    # Selecting the sentence/sentences that has the maximum score.

    max_score_value =max(sent_score_list)

    #Creating candidate list of sentences based on the maximum sent score

    for i in range(0, len(sentence_list)):
        if sent_score_list[i] == max_score_value:
            candidate_list.append((complete_sentence_list[i],i))

    #print 'Candidate list is :',candidate_list

    # Checking which of the scores is greater. IF score from sent_Score_list is greater than dateline score, then we find
    # the corresponding sentences and choose the best among them. Else we return the dateline as the result.
    if max_score_value > dateline_score:


        # Now we have to choose the best sentence among the sentences in candidate list

        if len(candidate_list)==1:

            temp_str= candidate_list[0][0]
            index=candidate_list[0][1]


        # If there are multiple candidates, then choose the sentence which appeared first in the story and then do the processing
        else:
            # There are more than one candidate sentences. Print the first sentence
            for k in range(0, len(candidate_list)):

                if month_list[candidate_list[k][1]] !=[]:                      #Rewarding sentences with month

                    #Cleaning up the candidate sentence
                    temp_str=candidate_list[k][0]
                    index=candidate_list[k][1]
                    break
                else:
                    temp_str=candidate_list[0][0]
                    index =candidate_list[0][1]

         #Cleaning up the candidate sentence
            # Replacing double quotes with blank and single quotes with "
            #temp_str=temp_str.replace('"','')
            #temp_str=temp_str.replace("'",'"')
            #temp_str=temp_str.replace(',','').replace('?','').replace('!','')

        ################### SENTENCE PROCESSING #######################

        result_list=[]
        answer_list=[]

        s_monthlist=month_list[index]
        s_timelist=time_list[index]

        #print 'Month list:',s_monthlist
        #print 'Time list:', s_timelist


        if s_monthlist == [] and s_timelist == []:    #The selected sentence does not seem to have a time or month expression, then print whole sentence  minus the words in the question
            for k in temp_str.split():
                if k not in temp_q:
                    result_list.append(k)

            return ' '.join(result_list)


        if s_monthlist!=[]:
            for i in range(0, len(s_monthlist)):
                if s_monthlist[i] not in temp_q :   #To counter situations where question has a month and NER doesn't identify it
                    answer_list.append(s_monthlist[i])


        # If time list is not empty
        if s_timelist != []:

            temp_list=temp_str.split()
            for j in range(0, len(temp_list)):
                if temp_list[j] in s_timelist and j!=0 and temp_list[j] not in temp_q:#and j!=len(temp_list)-1:
                    if temp_list[j-1] in stanford_stop_words_list:
                        answer_list.append(temp_list[j-1].lower())      #Appending the word before the time list which is generally a number or indicative of the time
                        if j-2 >=0:
                            answer_list.append(temp_list[j-2].lower())
                    else:
                        answer_list.append(temp_list[j-1].lower())      #Appending the word after the time list word which will be the result in few cases

            #Non-days time values
            for i in range(0, len(s_timelist)):
                if s_timelist[i] not in temp_q : #and s_timelist[i] not in ['days']:
                    answer_list.append(s_timelist[i])

            # Time list values will usually have numbers or other prepositions before it which will give us the complete answer
            time_prep=['over','period','within','inside','under','ago','through','past']

            for k in temp_str.split():
                if k.lower() in time_prep:
                    answer_list.append(k.lower())

                if k.isdigit():
                    answer_list.append(k)

                if k.lower() in time_nos:
                    answer_list.append(k.lower())

        #print 'Answer list is :',set(answer_list)

        temp_result=[]

        if answer_list != []:
           result=' '.join(list(set(answer_list)))
           return result

        else:
            for k in temp_str.split():
                if k not in temp_q:
                    temp_result.append(k)

            return ' '.join(temp_result)

    else:
        result=dateline
        return result

