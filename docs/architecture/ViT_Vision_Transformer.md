# Vision Transformer (ViT)

**Title:** An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale
**Authors:** Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby (Google Research, Brain Team)

## Abstract
While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. In vision, attention is either applied in conjunction with convolutional networks, or used to replace certain components of convolutional networks while keeping their overall structure in place. 

The authors show that this reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks. When pre-trained on large amounts of data and transferred to multiple mid-sized or small image recognition benchmarks (ImageNet, CIFAR-100, VTAB, etc.), Vision Transformer (ViT) attains excellent results compared to state-of-the-art convolutional networks while requiring substantially fewer computational resources to train.

## Method Overview
The approach splits an image into fixed-size patches, linearly embeds each of them, adds position embeddings, and feeds the resulting sequence of vectors to a standard Transformer encoder. In order to perform classification, the standard approach of adding an extra learnable "classification token" to the sequence is used.

### Key Takeaways
* **No convolutions required:** A pure Transformer architecture can be applied directly to image patches.
* **Pre-training scale:** ViT yields modest results on mid-sized datasets but truly excels when pre-trained on large-scale datasets (like JFT-300M or ImageNet-21k), trumping the inductive bias of CNNs.
* **Efficiency:** ViT attains state-of-the-art results while taking substantially fewer computational resources to train compared to large ResNets.
