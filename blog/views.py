from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from watson_developer_cloud import PersonalityInsightsV2


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='358aa707-ceee-4c84-96fa-475bc7d60516',
        password='YcL8Kwi0pF4o',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='a686258f-33d7-4c9d-87b2-dcf8818dcc10',
        password='MNODMlo1w2tQ')

    personality_insights = PersonalityInsightsV2(
        username='ac5b28fe-1560-478a-8a07-73ac020ef6d1',
        password='uQeUouVZaAAR')

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj = json.dumps(tone_analyzer.tone(tone_input=posting,
                                   content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']

        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='de')
        obj = json.dumps(translation, indent=2, ensure_ascii=False)
        post.obj2 = json.loads(obj)
        post.translate_spanish = post.obj2['translations'][0]['translation']#[0]['word_count'][0]['character_count']
        post.wordcount = post.obj2['word_count']
        post.charactercount = post.obj2['character_count']


        ## personality insights for extra credit

        profile = personality_insights.profile(text=post.text,
            content_type="text/plain", language='en')
        personObj = json.dumps(profile, indent=4, ensure_ascii=False)
        post.obj3 = json.loads(personObj)

        post.openness = post.obj3['tree']['children'][0]['children'][0]['children'][0]['percentage']
        post.conscientiousness = post.obj3['tree']['children'][0]['children'][0]['children'][1]['percentage']
        post.extraversion = post.obj3['tree']['children'][0]['children'][0]['children'][2]['percentage']
        post.agreeableness = post.obj3['tree']['children'][0]['children'][0]['children'][3]['percentage']

        post.personlity = post.obj3['tree']['children'][0]['children'][0]['children']
        post.pstring = ""
        for value in post.personlity:
            if value['percentage'] >= 0.5:
                name = value['name']
                percentage = str(value['percentage'])
                # post.needslist.append({'name': name, 'percentage': percentage})
                post.pstring += (name + " : " + percentage + " | ")

        for value in post.personlity:
            # if value['percentage'] >= 0.5:
            #     name = value['name']
            #     percentage = str(value['percentage'])
            #     # post.needslist.append({'name': name, 'percentage': percentage})
            #     post.pstring += (name + " : " + percentage + " | ")

            person = value['children']
            for i in person:
                if i['percentage'] >= 0.5:
                    name1 = i['name']
                    percentage1 = str(i['percentage'])
                    # post.needslist.append({'name': name, 'percentage': percentage})
                    post.pstring += (name1 + " : " + percentage1 + " | ")

        post.needs = post.obj3['tree']['children'][1]['children'][0]['children']
        # post.needslist = []
        post.needstring = ""
        for value in post.needs:
            if value['percentage'] >= 0.5:
                name = value['name']
                percentage = str(value['percentage'])
                # post.needslist.append({'name': name, 'percentage': percentage})
                post.needstring += (name + " : " + percentage + " | ")


        post.values = post.obj3['tree']['children'][2]['children'][0]['children']
        # post.valuelist = []
        post.valuestring = ""
        for value in post.values:
            if value['percentage'] >= 0.5:
                name = value['name']
                percentage = str(value['percentage'])
                # post.valuelist.append({'name':name,'percentage':percentage})
                post.valuestring += (name + " : " + percentage + " | ")

        # post.obj4 = post.obj3['tree']['children']
        #
        # for i in post.obj4:
        #     obj5 = post.obj4[i]['children']



    return render(request,'blog/post_list.html',{'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Post.objects.get(pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})