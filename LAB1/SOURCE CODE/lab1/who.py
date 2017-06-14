__author__ = 'Anirudh'

import WM
import NET
import nltk
import NER
import POS_Tagging
nltk.data.path.append("/home/anirudhn/nltk_data")
from nltk.stem.wordnet import WordNetLemmatizer

# The selection of answer is based on the sentence which gets the maximum total score across the four conditions ##

# But generally answers to "who" questions involve a person and so the maximum priority is given to them than other sentences


def answering_who(cleansedQuestion,stop_words_free_question,complete_sentence_list,sentence_list,sent_person_list,sent_prof_list):

    # Declaring globals to be used in this function

    sent_score_list=[]
    q_verblist=[]


    stanford_stop_words_list=['a','an','and','are','as','at','be','buy','do','for','from',
                          'has','have','he','in','is','it','its','of','on','that','the',
                          'to','was','were','will','with']

    temp_q=cleansedQuestion
    #temp_q=temp_q.replace('"','')
    #temp_q=temp_q.replace("'",'"')
    temp_q=temp_q.replace('?','')

    lmtzr=WordNetLemmatizer()
    pos_list= POS_Tagging.pos_tagging(temp_q)

    for i in range(0, len(pos_list)):
        if pos_list[i][1] in ['VB','VBD','VBZ','VBN'] and lmtzr.lemmatize(pos_list[i][0],'v') not in stanford_stop_words_list:
            q_verblist.append(lmtzr.lemmatize(pos_list[i][0],'v'))



    #print 'Temp_q: ',temp_q

    q_person_list,q_org_list,q_loc_list,q_month_list,q_time_list,q_money_list,q_percent_list,q_prof_list = NER.named_entity_recognition(temp_q)

    for i in range(0, len(complete_sentence_list)):
        #print 'Sentence is :', complete_sentence_list[i]
        score=0

        # 1. Score using word match rule. Match words in question with the words in stop free sentence

        #print 'Sentence is :',sentence_list[i]
        score=score + WM.stemWordMatch(cleansedQuestion,sentence_list[i])

        # 2. If question does not contain name but the answer contains NAME then you are confident(+6)
        if q_person_list==[]:

            #Giving more weights to sentences having more names in it
            if sent_person_list[i] !=[] or sent_prof_list[i] !=[]:
                #score=score + 6*len(sent_person_list) + 6* len(sent_prof_list)
                score=score + 6

            # 3. If question does not contain a name and answer contains the word "name" then good_clue (+4)
            lmtzr = WordNetLemmatizer()
            temp= complete_sentence_list[i].split()
            for k in range(0,len(temp)):
                if lmtzr.lemmatize(temp[k].lower())=='name':
                    score=score + 4

            #  4. Awards points to all sentences  that contain a name or reference to a human

            if sent_person_list[i] !=[] or sent_prof_list[i] !=[]:
                #score=score + 4*len(sent_person_list) + 4* len(sent_prof_list)
                score=score+4


        # 5. If the answer contains the exact verb found in the question after the "Who" or in fact in the whole question
        # then it is a confident clue and we reward it more

        sent_pos_list= POS_Tagging.pos_tagging(complete_sentence_list[i])

        '''for m in range(0, len(sent_pos_list)):
            if sent_pos_list[m][1] in ['VB','VBD','VBN','VBG','VBZ'] and sent_pos_list[m][0] in stop_words_free_question.split():
                score=score + 18
                #print 'Score now is :', score'''

        for k in range(0, len(sent_pos_list)):
            if sent_pos_list[k][1] in ['VB','VBD','VBZ','VBN'] and lmtzr.lemmatize(sent_pos_list[k][0],'v') in q_verblist:
                #print 'Verb in question and sentence matches'
                score=score + 6



        # 6. If the question contains a profession name, the answer has to be a person and sentence would have
        #the person name and the profession

        if q_prof_list!=[]:
            for k in complete_sentence_list[i].split():
                if k.lower() in q_prof_list:
                    #print 'Profession Yes !'
                    score=score+18

        else:  #Question contains name so the chances of answer being a profession name are decent
            if sent_prof_list[i] !=[]:
                score=score+6


        sent_score_list.append(score)

    #print 'Sent score list is :',sent_score_list


    # Selecting the sentence that has the maximum score. If it is a tie, we choose the sentence that appears first


    candidate_list=[]
    npfinal_list=[]
    temp_list=[]
    answer_list=[]

    max_score_value=max(sent_score_list)

    #print 'Max score is :',max_score_value

    for i in range(0, len(complete_sentence_list)):
        if sent_score_list[i]==max_score_value:
            candidate_list.append((complete_sentence_list[i],i))
    #print 'Candidate list is :',candidate_list


    #If there is only one sentence, then choose the sentence and then do the processing to display the answer

    if len(candidate_list)==1:

        temp_str= candidate_list[0][0]
        index=candidate_list[0][1]
        #Cleaning up the candidate sentence
        # Replacing double quotes with blank and single quotes with "
        #temp_str=temp_str.replace('"','')
        #temp_str=temp_str.replace("'",'"')
        #temp_str=temp_str.replace(',','').replace('?','').replace('!','')


    # If there are multiple candidates, then choose the sentence which appeared first in the story  and then do the processing
    else:
        # There are more than one candidate sentences. Print the first sentence
        for k in range(0, len(candidate_list)):

            #Cleaning up the candidate sentence

            temp_str=candidate_list[k][0]
            index =candidate_list[k][1]
            #temp_str=temp_str.replace('"','')
            #temp_str=temp_str.replace("'",'"')
            #temp_str=temp_str.replace(',','').replace('?','').replace('!','')


            break

    ####################### SENTENCE PROCESSING TO FIND THE ANSWER ###############################

    #Just pick out the noun-phrase or PERSON names from the sentence

    #s_plist,s_orglist,s_loclist,s_monthlist,s_timelist,s_moneylist,s_percentlist,s_proflist=NER.named_entity_recognition(temp_str)
    s_plist=sent_person_list[index]
    s_proflist=sent_prof_list[index]

    #print 'Prof list is:',s_proflist

    #If the question has a name of person, then the answer sentence should/would most probably
    #the name of a person but it should not be the name of the person appearing in the question.
    #If we can't find any other name in the candidate sentence then we do POS tagging and display the NOUN phrases

    #print 'Question person list is:',q_person_list
    #print 'Sentence person list is:',s_plist

    result_list=[]
    q_loc_who_list=[]

    if q_person_list==[] and s_plist==[]:   #If both the question does not have a name and the sentence does not have a name,print the whole sentence minus words which appear in question

        '''pos_np_list= POS_Tagging.pos_noun_tagging(temp_str)
        if pos_np_list != []:
            for x in pos_np_list:
                if x not in temp_q and x[0].isupper():   #Noun phrases or names generally start with an upper case character
                    print 'First character caps',x
                    result_list.append(x)
            return ' '.join(result_list)'''

        for k in temp_str.split():
            if k not in temp_q:
                result_list.append(k)

        return ' '.join(result_list)

    elif q_person_list !=[] and s_plist !=[]:    #To counter situations when both question and sentence has names Ex. Who defeated who ?
        for k in s_plist:
            if k not in temp_q:
                answer_list.append(k)


    elif q_person_list==[] and s_plist !=[]:
        for i in range(0, len(s_plist)):
            if s_plist[i] not in q_person_list and s_plist[i] not in temp_q:  #To counter situations where question has a name and NER doesn't identify it
                answer_list.append(s_plist[i])


    elif q_person_list != [] and s_proflist !=[]:  #To counter situations for 'Who is X' type questions which could have a profession name in the answer
        for k in s_proflist:
            answer_list.append(k)

    elif q_person_list==[] and q_loc_list !=[]: # Who is <X> where ?
        #print 'Question has no name but has a location'
        for k in temp_str.split():
            if k not in temp_q:
                q_loc_who_list.append(k)
        if q_loc_who_list !=[]:
            return ' '.join(q_loc_who_list)

    '''elif q_person_list==[] and s_proflist !=[]:
        for k in s_proflist:
            answer_list.append(k)'''

    if answer_list != [] :#and flag==1:                #Indicating candidate sentence has a name other than that in question
        result= ' '.join(answer_list)
    else:

        #Pick out the noun phrase or nouns and then display them as answer

        np_list = POS_Tagging.pos_noun_tagging(temp_str)
        for x in np_list :
            if x not in temp_q:
                npfinal_list.append(x) #Removing all occurences of existing noun phrases from the question


        #print 'NP Final list after removal is',npfinal_list
        if npfinal_list !=[]:
            result=' '.join(npfinal_list)

        else:
            result=temp_str                  # Printing out the whole sentence

    #print 'Result is:',result
    return result

