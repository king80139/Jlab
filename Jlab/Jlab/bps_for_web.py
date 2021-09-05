def Draw_Brand_Positioning_Map_Word2Vec(username, prname, input_directory):
    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    from gensim.models import Word2Vec
    from utils import Read_Arg_, import_dataframe

    ref, input_, output_, options = Read_Arg_(username, prname, 'Draw_Brand_Positioning_Map_Word2Vec', 2)

    brand_list = pd.read_csv(os.path.join(input_directory, ref)).iloc[:, 0].tolist()

    input_name = os.path.join(input_directory, input_)
    input_message = import_dataframe(input_name)
    token = [line.split(' ') for line in input_message['contents']]

    dim = options[0]
    pa = options[1]

    print('Embedding.....')
    model = Word2Vec(token, size=dim, window=6, min_count=30, workers=4, sg=1)
    model.init_sims(replace=True)
    word_vectors = model.wv
    vocabs = [key for key in word_vectors.vocab.keys()]
    arr = [word_vectors[v] for v in vocabs]

    if dim > 3:
        print('Running PCA.....')
        from sklearn.decomposition import PCA
        pca = PCA(n_components = pa)
        if pa:
            if pa == 2:
                xy = pca.fit_transform(arr)
                x = xy[:, 0]
                y = xy[:, 1]
            elif pa == 3:
                xyz = pca.fit_transform(arr)
                x = xyz[:, 0]
                y = xyz[:, 1]
                z = xyz[:, 2]
            else:
                print('pa must be 2 or 3')
        else:
            print('enter pa')
    else:
        x = [word_vectors[v][0] for v in vocabs]
        y = [word_vectors[v][1] for v in vocabs]
        if dim == 3:
            z = [word_vectors[v][2] for v in vocabs]

    print('Drawing plot.....')
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    for brand in brand_list:
        try:
            i = vocabs.index(brand)
        except:
            print('%s is not in words' %brand)
        if (dim == 2) or (pa == 2):
            plt.scatter(x[i], y[i], marker='o')
            plt.annotate(brand, xy=(x[i], y[i]))
        elif (dim == 3) or (pa == 3):
            ax = plt.subplot(111, projection='3d')
            ax.scatter(x[i], y[i], z[i], marker='o')
            ax.text(x[i], y[i], z[i], brand)

    plt.show()
    plt.savefig(os.path.join(input_directory, output_))

##############################################################################

def Draw_What_To_Say_About_Single_Brand_Map(username, prname, input_directory):
    import os
    import matplotlib.pyplot as plt
    from gensim.models import Word2Vec
    from utils import Read_Arg_, import_dataframe

    ref, input_, output_, options = Read_Arg_(username, prname, 'Draw_What_To_Say_About_Single_Brand_Map', 3)

    keyBrand = str(ref)

    input_name = os.path.join(input_directory, input_)
    input_message = import_dataframe(input_name)

    token = [line.split(' ') for line in input_message['contents']]

    num = options[0]
    dim = options[1]
    pa = options[2]

    print('Embedding.....')
    model = Word2Vec(token, size=dim, window=6, min_count=30, workers=4, sg=1)
    model.init_sims(replace=True)
    word_vectors = model.wv
    vocabs = [key for key in word_vectors.vocab.keys()]
    arr = [word_vectors[v] for v in vocabs]

    if dim > 3:
        print('Running PCA.....')
        from sklearn.decomposition import PCA
        pca = PCA(n_components = pa)
        if pa:
            if pa == 2:
                xy = pca.fit_transform(arr)
                x = xy[:, 0]
                y = xy[:, 1]
            elif pa == 3:
                xyz = pca.fit_transform(arr)
                x = xyz[:, 0]
                y = xyz[:, 1]
                z = xyz[:, 2]
            else:
                print('pa must be 2 or 3')
        else:
            print('enter pa')
    else:
        x = [word_vectors[v][0] for v in vocabs]
        y = [word_vectors[v][1] for v in vocabs]
        if dim == 3:
            z = [word_vectors[v][2] for v in vocabs]

    print('Drawing plot.....')
    fig = plt.figure(figsize=(10, 9))
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    try:
        i = vocabs.index(keyBrand)
    except:
        print('%s is not in words' % keyBrand)
    if (dim == 2) or (pa == 2):
        plt.scatter(x[i], y[i], marker='o')
        plt.annotate(keyBrand, xy=(x[i], y[i]))
        for similar_word in word_vectors.most_similar(keyBrand, topn=num):
            iw = vocabs.index(similar_word[0])
            plt.scatter(x[iw], y[iw], marker='o')
            plt.annotate(similar_word[0], xy=(x[iw], y[iw]))
    elif (dim == 3) or (pa == 3):
        ax = plt.subplot(111, projection='3d')
        ax.scatter(x[i], y[i], z[i], marker='o')
        ax.text(x[i], y[i], z[i], keyBrand)
        for similar_word in word_vectors.most_similar(keyBrand, topn=num):
            iw = vocabs.index(similar_word[0])
            ax.scatter(x[iw], y[iw], z[iw], marker='o')
            ax.text(x[iw], y[iw], z[iw], similar_word[0])

    plt.show()
    plt.savefig(os.path.join(input_directory, output_))