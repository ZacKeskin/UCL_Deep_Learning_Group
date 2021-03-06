import os
import tensorflow as tf
import numpy as np
import datetime
from utils import *
import imghdr
import pdb

version = 'NewFaces'
#helper function to perform leaky relu operations
def lrelu(x, n, leak=0.2): 
            return tf.maximum(x, leak * x, name=n) 

def Tensorfy_images(dir,HEIGHT,WIDTH,CHANNEL, BATCH_SIZE):   
   
    #get the current directory passed to the function. 
    target_dir = os.path.join(os.getcwd(),dir)
    
    images = [] #create an empty array to store the images

    #for each item in the data folder...put that image into the images array    
    for each in os.listdir(target_dir):
        if imghdr.what(os.path.join(target_dir,each)) == 'jpeg':
            images.append(os.path.join(target_dir,each))

    # Convert all the images in the images array to tensors (strings)
    all_images = tf.convert_to_tensor(images, dtype = tf.string)
    
    # Create a list of tensors one for each tensor (image)
    images_queue = tf.train.slice_input_producer([all_images])
    # Reads all the images in the queue and outputs them into 'content'                                   
    content = tf.read_file(images_queue[0])
    # Takes a jpeg encoded image which is of the type tf.string and decodes it to a proper image. Furthermore add the colour to the image (coloured images have 3 channels Red, Green, Blue)
    image = tf.image.decode_jpeg(content, channels = CHANNEL)
    # Image altering features   
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, max_delta = 0.1)
    image = tf.image.random_contrast(image, lower = 0.9, upper = 1.1)

    # Resize the image
    size = [HEIGHT, WIDTH]
    image = tf.image.resize_images(image, size)
    # Set the shape of the image to a 64*64*3 image
    image.set_shape([HEIGHT,WIDTH,CHANNEL])

    # Returns a tensor with the desired shape to image
    image = tf.cast(image, tf.float32)

    image = image / 255.0
    # List of tensors in desired batch size
    images_batch = tf.train.shuffle_batch(
                                    [image], batch_size = BATCH_SIZE,
                                    num_threads = 4, capacity = 200 + 3* BATCH_SIZE,
                                    min_after_dequeue = 200)
    # Number of images in the dataset
    num_images = len(images)
    # Return the image batch and the number of images

    return images_batch, num_images

#FOR TEST FUNCTION
#in current dir, create folder Test with input.jpg and target.jpg

def test_import_data(dir, HEIGHT,WIDTH,CHANNEL, BATCH_SIZE):  
    
    #get the current directory we are in. 
    current_dir = os.getcwd()
    target_img = os.path.join(current_dir, dir)
    
    
    # Convert all the images in the images array to tensors (strings)
    image = tf.convert_to_tensor(target_img, dtype = tf.string)
    

   

   # images_queue = tf.train.slice_input_producer(image)
    # Reads all the images in the queue and outputs them into 'content'                                   
    content = tf.read_file(image)
   
    # Takes a jpeg encoded image which is of the type tf.string and decodes it to a proper image. Furthermore add the colour to the image (coloured images have 3 channels Red, Green, Blue)
    image = tf.image.decode_jpeg(content, channels = CHANNEL)
    # Image altering features   
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, max_delta = 0.1)
    image = tf.image.random_contrast(image, lower = 0.9, upper = 1.1)

    # Resize the image
    size = [HEIGHT, WIDTH]
    image = tf.image.resize_images(image, size)
    # Set the shape of the image to a 64*64*3 image
    image.set_shape([HEIGHT,WIDTH,CHANNEL])

    # Returns a tensor with the desired shape to image
    image = tf.cast(image, tf.float32)

    image = image / 255.0
    images = tf.train.shuffle_batch(
                                    [image], batch_size = BATCH_SIZE,
                                    num_threads = 4, capacity =64,
                                    min_after_dequeue = 1)
    
    return images


class Generator():
    def __init__(self, kernel_size, channel, scope):
        self.c2, self.c4, self.c8, self.c16 = 32, 64, 128, 256  # channel num: 64, 128, 256, 512

        self.output_dim = channel
        self.kernel_size = kernel_size
        self.channel = channel
        self.scope = scope

    def connect(self,input, is_train, reuse=False):
        with tf.variable_scope(self.scope) as scope:
            if reuse:
                scope.reuse_variables()
    
        # Convolution, batch normalisation, activation, dropout, repeat! 

            # Layer 1
            conv1 = tf.layers.conv2d(input, self.c2, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv1')
           
            act1 = lrelu(conv1, n='act1')
           

            # Layer 2
            conv2 = tf.layers.conv2d(act1, self.c4, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv2')
            bn2 = tf.contrib.layers.batch_norm(conv2, is_training=is_train, epsilon=1e-5, decay = 0.9,  updates_collections=None, scope='bn2')
            act2 = lrelu(bn2, n='act2')
          
            
            # Layer 3
            conv3 = tf.layers.conv2d(act2, self.c8, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv3')
            bn3 = tf.contrib.layers.batch_norm(conv3, is_training=is_train, epsilon=1e-5, decay = 0.9,  updates_collections=None, scope='bn3')
            act3 = lrelu(bn3, n='act3')
            
            
            # Layer 4
            conv4 = tf.layers.conv2d(act3, self.c16, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv4')
            bn4 = tf.contrib.layers.batch_norm(conv4, is_training=is_train, epsilon=1e-5, decay = 0.9,  updates_collections=None, scope='bn4')
            act4 = lrelu(bn4, n='act4')
           

        # Deconvolution, batch normalisation, activation, repeat! 

            # Layer 5
            conv5 = tf.layers.conv2d_transpose(act4, self.c8, kernel_size=self.kernel_size, strides =[2,2], padding = "SAME", 
                                            kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name ='conv5')
            bn5 = tf.contrib.layers.batch_norm(conv5, is_training=is_train, epsilon=1e-5, decay =0.9, updates_collections=None, scope='bn5')
            act5 = tf.nn.relu(bn5, name='act5')
            
            # Layer 6
            conv6 = tf.layers.conv2d_transpose(act5, self.c4, kernel_size=self.kernel_size, strides =[2,2], padding = "SAME", 
                                            kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name ='conv6')
            bn6 = tf.contrib.layers.batch_norm(conv6, is_training=is_train, epsilon=1e-5, decay =0.9, updates_collections=None, scope='bn6')
            act6 = tf.nn.relu(bn6, name='act6')
            
            # Layer 7
            conv7 = tf.layers.conv2d_transpose(act6, self.c2, kernel_size=self.kernel_size, strides =[2,2], padding = "SAME", 
                                            kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name ='conv7')
            bn7 = tf.contrib.layers.batch_norm(conv7, is_training=is_train, epsilon=1e-5, decay =0.9, updates_collections=None, scope='bn7')
            act7 = tf.nn.relu(bn7, name='act7')

            # Layer 8
            output_dim = self.channel
            conv8 = tf.layers.conv2d_transpose(act7, output_dim, kernel_size=self.kernel_size, strides =[2,2], padding = "SAME", 
                                            kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name ='conv8')
            
            act8 = tf.nn.relu(conv8, name='act8')

            output = act8
            return output# Return generated image (eventually we want this generator to take in one image and output another that's what we're training it to do)

class Discriminator():
    def __init__(self,kernel_size, channel, scope):
        self.c2, self.c4, self.c8, self.c16 = 32, 64, 128, 256  # channel num: 64, 128, 256, 512

        self.kernel_size = kernel_size
        self.channel=channel
        self.scope = scope

    def connect(self, input, is_train, reuse=False):
        
        with tf.variable_scope(self.scope) as scope:
            if reuse:
                scope.reuse_variables()
        
        
        # Convolution, batch normalisation, activation, repeat! 

            # Layer 1
            conv1 = tf.layers.conv2d(input, self.c2, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv1')
           
            act1 = lrelu(conv1, n='conv1')

            # Layer 2
            conv2 = tf.layers.conv2d(act1, self.c4, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv2')
            bn2 = tf.contrib.layers.batch_norm(conv2, is_training=is_train, epsilon=1e-5, decay = 0.9,  updates_collections=None, scope='bn2')
            act2 = lrelu(bn2, n='act2')
            
            # Layer 3
            conv3 = tf.layers.conv2d(act2, self.c8, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv3')
            bn3 = tf.contrib.layers.batch_norm(conv3, is_training=is_train, epsilon=1e-5, decay = 0.9,  updates_collections=None, scope='bn3')
            act3 = lrelu(bn3, n='act3')
            
            # Layer 4
            conv4 = tf.layers.conv2d(act3, self.c16, kernel_size=self.kernel_size, strides=[2, 2], padding="SAME",
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.02), name='conv4')
            bn4 = tf.contrib.layers.batch_norm(conv4, is_training=is_train, epsilon=1e-5, decay = 0.9,  updates_collections=None, scope='bn4')
            act4 = lrelu(bn4, n='act4')
        
            # Start from act4
            dim = int(np.prod(act4.get_shape()[1:]))
            # Convert the 4*4*256 tensor into a flat and fully connected layer
            fc1 = tf.reshape(act4, shape=[-1, dim], name='fc1')
        
            # Initialise random weight variables
            w2 = tf.get_variable('w2', shape=[fc1.shape[-1], 1], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
            # Initialise random bias variables
            b2 = tf.get_variable('b2', shape=[1], dtype=tf.float32, initializer=tf.constant_initializer(0.0))

            # Multiply the weights by the fully connected layer add the biases (multiplying 4096 row vector by 4096 column vector giving 1 number )
            logits = tf.add(tf.matmul(fc1, w2), b2, name='logits')
            # Perform sigmoid on the one number putting the value of the number between 0 and 1.
            acted_out = tf.nn.sigmoid(logits)

            return logits #return a value between 0 and 1


class GAN():

    def __init__(self, GANtype, kernel_size=[4,4], channel=3):
        
        
        valid = ['Standard','RecLoss','Discogan']
        if GANtype.upper() not in (v.upper() for v in valid):
            raise ValueError("GANtype must be one of %r." % valid)
        else:
            self.GANtype = GANtype

        if not (isinstance(kernel_size,(list,tuple)) and len(kernel_size)==2):
            raise ValueError("Kernel_Size must be a list containing two elements") #should probably check for positive ints too
        else:
            self.kernel_size = kernel_size


        self.kernel_size = kernel_size
        self.channel=channel

    def train(self, 
                input_dir=os.path.join(os.getcwd(),'input'), 
                target_dir=os.path.join(os.getcwd(),'target'), 
                batch_size=16, 
                n_epochs=1,
                img_height=64,
                img_width=64,
                img_channels=3,
                output_dir=os.getcwd(),
                checkpoint_after_epoch=1):  #optimiser,loss, 
        #self.batch_size = batch_size
        #self.n_epochs = n_epochs

        output_dir = os.path.join(output_dir, self.GANtype)
        input_batch, input_count = Tensorfy_images(input_dir,img_height,img_width,img_channels,batch_size)
        target_batch, target_count = Tensorfy_images(target_dir,img_height,img_width,img_channels,batch_size)
        batch_count = int(input_count / batch_size) 
        total_batch = 0
        
        with tf.variable_scope('input'):
                # Real image placeholder
                input_image = tf.placeholder(tf.float32, shape = [None, img_height, img_width, img_channels])
                # Fake image placeholder
                target_image = tf.placeholder(tf.float32, shape = [None, img_height, img_width, img_channels])
                is_train = tf.placeholder(tf.bool, name='is_train')

        # Define these upfront before being assigned
        #train_image = 0
        #train_image2 = 0

        # ------ Model-Specific Training Steps------- #

        if self.GANtype.upper() == "STANDARD": 
            print('\n Training Standard GAN \n')
            
            G1 = Generator(kernel_size=self.kernel_size, channel=img_channels, scope='Gen1')
            D1 = Discriminator(kernel_size=self.kernel_size, channel=img_channels, scope='Dis1')

            # Let the Generator create a fake image based on the Target Data
            fake_image = G1.connect(target_image, is_train)

            # Feed the real image into the discriminator 
            real_result = D1.connect(input_image, is_train)
            # Feed the output of the generator into the discriminator
            fake_result = D1.connect(fake_image, is_train, reuse=True)

            # Calculate the loss between the generated image and real image
            with tf.name_scope('D_loss'):    
                d_loss = tf.reduce_mean(fake_result) - tf.reduce_mean(real_result)  # This optimizes the discriminator.
            with tf.name_scope('G_loss'):    
                g_loss = -tf.reduce_mean(fake_result)  # This optimizes the generator.

            #for TensorBoard PATH

            logs_name= 'logFolder_for_' +  'STANDARD'
            logs_path=os.path.join('logFolder',logs_name)
            
            #TENSORBOARD SCALARS
            tf.summary.scalar("Generator Loss", g_loss)
            tf.summary.scalar("Discriminator Loss", d_loss)
            
        
            

        
            

        elif self.GANtype.upper() == "RECLOSS":
            print('\n Training GAN with Reconstruction Loss \n')
            
            
            G1 = Generator(self.kernel_size,self.channel, scope = 'Gen1')
            G2 = Generator(self.kernel_size,self.channel, scope = 'Gen2')
            D1 = Discriminator(kernel_size=self.kernel_size, channel=img_channels, scope = 'Dis1')

            # Let the Generators create a fake image based on the Target Data
            fake_image = G1.connect(target_image, is_train)
            reconstructed_image = G2.connect(fake_image, is_train)
            #feed the real image into the discriminator 
            real_result = D1.connect(input_image, is_train)
            #feed the output of the generator into the disccriminator
            fake_result = D1.connect(fake_image, is_train, reuse=True)

            #reconstructed loss
            with tf.name_scope('R_loss'):    
                reconstructed_loss=tf.metrics.mean_squared_error(target_image, reconstructed_image)
            
            # Calculate the loss between the generated image and real image
            with tf.name_scope('D_loss'):    
                d_loss = tf.reduce_mean(fake_result) - tf.reduce_mean(real_result)  # This optimizes the discriminator.
            with tf.name_scope('G_loss'):    
                g_loss = -tf.reduce_mean(fake_result) + tf.reduce_mean(reconstructed_loss) # This optimizes the generator.
            
            
            #for TensorBoard PATH

            logs_name= 'logFolder_for_' +  'RECLOSS'
            logs_path=os.path.join('logFolder',logs_name)
            
            #TENSORBOARD SCALARS
            tf.summary.scalar("Generator Loss", g_loss)
            tf.summary.scalar("Discriminator Loss", d_loss)
            tf.summary.scalar("Reco Loss", tf.reduce_mean(reconstructed_loss))
            merged_summary_op = tf.summary.merge_all()


        elif self.GANtype.upper() == "DISCOGAN":
            print('Training DiscoGAN')
            
            G1 = Generator(self.kernel_size,self.channel, scope = 'Gen1')
            G2 = Generator(self.kernel_size,self.channel, scope = 'Gen2')
            D1 = Discriminator(kernel_size=self.kernel_size, channel=img_channels, scope = 'Dis1')
            D2 = Discriminator(kernel_size=self.kernel_size, channel=img_channels, scope = 'Dis2')


            fake_image = G1.connect(input_image, is_train)
            fake_target_image = G2.connect(target_image, is_train)


            reconstructed_input_image = G2.connect(fake_image, is_train, reuse=True)

            reconstructed_target_image = G1.connect(fake_target_image, is_train, reuse=True)
            
            #feed the real input image into discriminator (1)
            real_input_result = D1.connect(input_image, is_train)
            #feed the output of generator2 into discriminator (1)
            fake_input_result = D1.connect(fake_image, is_train, reuse=True)

            #feed the real male image into the discriminator (2)
            real_target_result = D2.connect(target_image, is_train)
            #feed the output of generator (1) into disccriminator (2)
            fake_target_result = D2.connect(fake_target_image, is_train, reuse=True)

            #reconstructed loss
            reconstructed_input_loss = tf.metrics.mean_squared_error(input_image, reconstructed_input_image)
            reconstructed_target_loss = tf.metrics.mean_squared_error(target_image, reconstructed_target_image)


            #calculate the loss between the generated image and real image
            
            d_input_loss = tf.reduce_mean(fake_input_result) - tf.reduce_mean(real_input_result)  # This optimizes discriminator (1).
            d_target_loss = tf.reduce_mean(fake_target_result) - tf.reduce_mean(real_target_result)  # This optimizes discriminator (2).
            
           

            with tf.name_scope('D_loss'):    
                d_loss = d_input_loss + d_target_loss

            generator_loss = -(tf.reduce_mean(fake_target_result)  +tf.reduce_mean(fake_input_result)) # This optimizes the generators.
            
            with tf.name_scope('R_loss'):    
                reconstructed_loss = tf.reduce_mean(reconstructed_target_loss) + tf.reduce_mean(reconstructed_input_loss) # This optimizes the generators.
            
            with tf.name_scope('G_loss'):    
                g_loss= generator_loss + reconstructed_loss

            #for TensorBoard PATH

            logs_name= 'logFolder_for_' +  'DISCO'
            logs_path=os.path.join('logFolder',logs_name)
            
            #TENSORBOARD SCALARS
            tf.summary.scalar("Generator Loss", g_loss)
            tf.summary.scalar("Discriminator Loss", d_loss)
            tf.summary.scalar("Reco Loss", reconstructed_loss)
            merged_summary_op = tf.summary.merge_all()


        # ------ Training Steps Applicable to all Models ------- #

        #returns a list of trainable variables (likes weights and biases)
        t_vars = tf.trainable_variables()
        #trainable discriminator variables are stored in d_vars
        d_vars = [var for var in t_vars if 'Dis' in var.name]
        #trainable generator variables are stored in g_vars
        g_vars = [var for var in t_vars if 'Gen' in var.name]
    
        #minmise the d_loss using the rms optimizer by altering the discriminator weights and biases      
        trainer_d = tf.train.AdamOptimizer(learning_rate=2e-4, beta1=0.5,beta2=0.999,epsilon=0.1).minimize(d_loss, var_list=d_vars)
        trainer_g = tf.train.AdamOptimizer(learning_rate=2e-4, beta1=0.5,beta2=0.999,epsilon=0.1).minimize(g_loss, var_list=g_vars)
        # clip discriminator weights between the values -0.01 and 0.01
        d_clip = [v.assign(tf.clip_by_value(v, -0.01, 0.01)) for v in d_vars]

       

        sess = tf.Session()
        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint('./model/' + version)

        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())

        
        save_path = saver.save(sess, "/tmp/model.ckpt")
        #uncomment to load the latest weights of the model.
        #saver.restore(sess, tf.train.latest_checkpoint('./model/NewFaces/'))
        print(sess, tf.train.latest_checkpoint('./model/NewFaces/'))
        # Initialise the variables
        

        #summary_writer = tf.summary.FileWriter(logs_path, sess.graph)
        #merged_summary_op = tf.summary.merge_all()
        
        # Prepare Checkpoint
        

        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)

        print('total training sample num:%d' % input_count)
        print('batch size: %d, batch num per epoch: %d, epoch num: %d' % (batch_size, batch_count, n_epochs))
        print('start training...')

        #pdb.set_trace()
        for i in range(n_epochs):
            print('\n Epoch: ' + str(i+1) + ' of ' + str(n_epochs)) #i+1 due to python's zero-indexing
            for j in range(batch_count):
                print('\n Batch: ' + str(j+1) + ' of ' + str(batch_count)) #i+1 due to python's zero-indexing
                d_iters = 4
                g_iters = 1

                
                # Update the discriminator
                for k in range(d_iters):
                    train_image = sess.run(input_batch)
                    train_image2 = sess.run(target_batch)
                    sess.run(d_clip)
                    if self.GANtype.upper() == 'DISCOGAN':
                        d_feed_dict = {target_image: train_image2, input_image: train_image, is_train: True}
                       
                    else:        
                        d_feed_dict = {target_image: train_image2, input_image: train_image, is_train: True}
                        
                    
                    _, dLoss = sess.run([trainer_d, d_loss],feed_dict = d_feed_dict)

                # Update the generator
                for k in range(g_iters): 
                    train_image = sess.run(input_batch)
                    train_image2 = sess.run(target_batch)
                    
                    if self.GANtype.upper() == 'DISCOGAN':
                        g_feed_dict = {input_image: train_image, target_image: train_image2,  is_train: True}
                        
                    else:        
                        g_feed_dict = {target_image: train_image2, is_train: True}
                        

                    _, gLoss= sess.run([trainer_g, g_loss],feed_dict = g_feed_dict)   
                    #summary =sess.run(merged_summary_op,feed_dict = d_feed_dict)
                    #summary_writer.add_summary(summary,i*batch_count +j)
         
                
                
            # Save check point every n epochs
            if (i+1)%checkpoint_after_epoch == 0:
                if not os.path.exists('./model/' + version):
                    os.makedirs('./model/' + version)
                saver.save(sess, './model/' +version + '/' + str(i))  
            if (i+1)%1 == 0:
                # save images every 10 epochs
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                #retrieve a sample of images produced by the generator and discriminator
                if self.GANtype.upper() == 'DISCOGAN':
                    imgtestG = sess.run(fake_image, feed_dict=g_feed_dict)
                    imgtestD = sess.run(fake_target_image,feed_dict=d_feed_dict)
                #save the images into the output directory. 
                    save_images(imgtestG, [8,8] ,output_dir + '/Gen_image_epoch' + str(i+1) + '.jpg')
                    save_images(imgtestD, [8,8] ,output_dir + '/Dis_image_epoch' + str(i+1) + '.jpg')
                else:
                    imgtestG = sess.run(fake_image, feed_dict=g_feed_dict)
                    save_images(imgtestG, [8,8] ,output_dir + '/Gen_image_epoch' + str(i+1) + '.jpg')

                

                print('train:[%d],d_loss:%f,g_loss:%f' % (i+1, dLoss, gLoss))


        coord.request_stop()
        coord.join(threads)

    
    # TEST the model
    def test(self,height,width,channel,testfolder, resultname, input_image_name, target_image_name):
        current_dir = os.getcwd()
        self.testfolder = testfolder
        self.resultname = resultname
        self.input_image_name = input_image_name
        self.target_image_name = target_image_name
        tf.reset_default_graph()
        
        #placeholder variables for the test input image and test target image
        with tf.variable_scope('input'):
             test_input = tf.placeholder(tf.float32, shape = [None,height, width, channel], name='test_input')
             test_target = tf.placeholder(tf.float32, shape=[None,height, width, channel], name='test_target')
             is_train = tf.placeholder(tf.bool, name='is_train')
        #
        result_path=[]
        for i in range (1,5):
            result_path.append(os.path.join(current_dir, self.testfolder + '/' + self.resultname + str(i) +'.jpg'))
        
        


        res_input, res_target=test_import_data(self.testfolder + '/' + self.input_image_name + '.jpg',height,width,channel,1), test_import_data(self.testfolder + '/' + self.target_image_name + '.jpg',height,width,channel,1)
        

        G1 = Generator(kernel_size=self.kernel_size, channel=channel, scope='Gen1')
        G2 = Generator(self.kernel_size,channel, scope = 'Gen2')

        
        # Let the Generator create a fake image based on the Target Data 
        output=[]
        
        output1=G1.connect(test_input,is_train)
        output.append(output1)
        output2=G2.connect(test_input,is_train)
        output.append(output2)
        output3=G1.connect(test_target,is_train,reuse=tf.AUTO_REUSE)
        output.append(output3)
        output4=G2.connect(test_target,is_train,reuse=tf.AUTO_REUSE)
        output.append(output4)
        print("output")
        
        #saver = tf.train.Saver()
        with tf.Session() as sess:
            saver = tf.train.Saver()
            ckpt = tf.train.latest_checkpoint('./model/' + version)
            sess.run(tf.global_variables_initializer())
            sess.run(tf.local_variables_initializer())
            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(sess=sess, coord=coord)

            
            
            
            

            #RESTORE
            #reload weights from the latest checkpoint
            saver.restore(sess, tf.train.latest_checkpoint('./model/NewFaces/'))
       

           
              
            res1=sess.run(res_input)
            res2=sess.run(res_target)
        
            img=[]
            for i in range (0,4):
                res=sess.run(output[i],feed_dict={test_input: res1, test_target: res2,is_train: False})
                img.append(res)
            
            

            print("before")
            for i in range (0,4):
                save_images(img[i], [8,8], result_path[i])
            
            
            print("after")
            
            coord.request_stop()
            coord.join(threads)