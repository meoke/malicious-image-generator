import numpy as np
from keras import backend as K
from keras.applications import inception_v3

from src.Utils import Utils


class Keras:
    def __init__(self, classes_csv_path, class_name_to_fake):
        self.classname_to_id = Utils.load_classes_csv(classes_csv_path)
        self.class_name_to_fake = class_name_to_fake
        self.grab_cost_from_model = self.init_keras()

    def init_keras(self):
        # Load pre-trained image recognition model
        model = inception_v3.InceptionV3()
        # Grab a reference to the first and last layer of the neural net
        model_input_layer = model.layers[0].input
        model_output_layer = model.layers[-1].output

        # Define the cost function.
        # Our 'cost' will be the likelihood out image is the target class according to the pre-trained model
        cost_function = model_output_layer[0, self.classname_to_id[self.class_name_to_fake]]

        # We'll ask Keras to calculate the gradient based on the input image and the currently predicted class
        # In this case, referring to "model_input_layer" will give us back image we are hacking.
        # gradient_function = K.gradients(cost_function, model_input_layer)[0]

        # Create a Keras function that we can call to calculate the current cost and gradient
        return K.function([model_input_layer, K.learning_phase()],
                          [cost_function])

    @staticmethod
    def get_prediction(img):
        # Load pre-trained image recognition model
        model = inception_v3.InceptionV3()  # todo wyrzucić jako pole klasy? Bo nie zmieniamy nigdzie samego modelu?

        # Add a 4th dimension for batch size (as Keras expects)
        img_array = np.expand_dims(img, axis=0)

        # Run the image through the neural network
        predictions = model.predict(img_array)

        # Convert the predictions into text and print them
        predicted_classes = inception_v3.decode_predictions(predictions, top=1)
        imagenet_id, name, confidence = predicted_classes[0][0]
        print("This is a {} with {:.4}% confidence!".format(name, confidence * 100))

    def get_prediction_on_custom_class(self, img):
        # Add a 4th dimension for batch size (as Keras expects)
        img_array = np.expand_dims(img, axis=0)

        cost = self.grab_cost_from_model([img_array, 0])[0]
        # print("Model's predicted likelihood that the image is a {}: {:.8}%".format(self.class_name_to_fake, cost * 100))
        return cost * 100

    def get_class_id(self, class_name):
        return self.classname_to_id[class_name]
