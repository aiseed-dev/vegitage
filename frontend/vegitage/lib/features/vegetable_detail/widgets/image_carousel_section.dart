// lib/features/vegetable_detail/widgets/image_carousel_section.dart

import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:vegitage/core/providers/providers.dart';
import 'package:vegitage/core/models/vegetable_image.dart';

class ImageCarouselSection extends StatefulWidget {
  const ImageCarouselSection({
    super.key,
    required this.hasImages,
    required this.imageId,
    required this.imageCategory,
  });

  final bool hasImages;
  final String imageId;
  final String imageCategory;

  @override
  State<ImageCarouselSection> createState() => _ImageCarouselSectionState();
}

class _ImageCarouselSectionState extends State<ImageCarouselSection> {
  List<VegetableImage>? _imageInfoList;
  bool _isLoading = true;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _loadImageInfo();
  }

  Future<void> _loadImageInfo() async {
    if (!widget.hasImages) {
      setState(() {
        _isLoading = false;
      });
      return;
    }

    try {
      final imageInfoList = await imageService.getImageInfo(
        widget.imageId,
        widget.imageCategory,
      );
      if (mounted) {
        setState(() {
          _imageInfoList = imageInfoList;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _hasError = true;
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.hasImages) {
      return const SizedBox.shrink();
    }

    if (_isLoading) {
      return const _LoadingPlaceholder();
    }

    if (_hasError) {
      return const _ErrorPlaceholder();
    }

    if (_imageInfoList == null || _imageInfoList!.isEmpty) {
      return const SizedBox.shrink();
    }

    if (_imageInfoList!.length == 1) {
      final imageUrl =
          "https://aiseed.page/images/${widget.imageCategory}/${widget.imageId}/${_imageInfoList!.first.filename}";
      return _SingleStaticImage(
        imageUrl: imageUrl,
        caption: _imageInfoList!.first.caption,
      );
    }

    return _ManualCarousel(
      imageId: widget.imageId,
      imageCategory: widget.imageCategory,
      imageInfoList: _imageInfoList!,
    );
  }
}

class _ManualCarousel extends StatefulWidget {
  const _ManualCarousel({
    required this.imageId,
    required this.imageCategory,
    required this.imageInfoList,
  });

  final String imageId;
  final String imageCategory;
  final List<VegetableImage> imageInfoList;

  @override
  State<_ManualCarousel> createState() => _ManualCarouselState();
}

class _ManualCarouselState extends State<_ManualCarousel> {
  final PageController _pageController = PageController();
  int _currentImageIndex = 0;

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final imageUrls = widget.imageInfoList.map((info) {
      return Uri.parse('https://aiseed.page')
          .replace(pathSegments: [
            'images',
            widget.imageCategory,
            widget.imageId,
            info.filename
          ])
          .toString();
    }).toList();

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Column(
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                height: 250.0,
                child: PageView.builder(
                  controller: _pageController,
                  itemCount: imageUrls.length,
                  itemBuilder: (context, index) {
                    return _buildSingleImage(imageUrls[index]);
                  },
                  onPageChanged: (index) {
                    setState(() {
                      _currentImageIndex = index;
                    });
                  },
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new,
                        color: Colors.white, size: 20),
                    onPressed: () {
                      _pageController.previousPage(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                      );
                    },
                    style: IconButton.styleFrom(
                        backgroundColor: Colors.black.withOpacity(0.4)),
                  ),
                  IconButton(
                    icon: const Icon(Icons.arrow_forward_ios,
                        color: Colors.white, size: 20),
                    onPressed: () {
                      _pageController.nextPage(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                      );
                    },
                    style: IconButton.styleFrom(
                        backgroundColor: Colors.black.withOpacity(0.4)),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          _buildCaptionAndIndicator(context),
        ],
      ),
    );
  }

  Widget _buildCaptionAndIndicator(BuildContext context) {
    final currentCaption = widget.imageInfoList[_currentImageIndex].caption;

    return Column(
      children: [
        if (currentCaption != null && currentCaption.isNotEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              currentCaption,
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: widget.imageInfoList.asMap().entries.map((entry) {
            return GestureDetector(
              onTap: () {
                _pageController.animateToPage(
                  entry.key,
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeInOut,
                );
              },
              child: Container(
                width: 8.0,
                height: 8.0,
                margin:
                    const EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: (Theme.of(context).brightness == Brightness.dark
                          ? Colors.white
                          : Colors.black)
                      .withOpacity(_currentImageIndex == entry.key ? 0.9 : 0.3),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class _SingleStaticImage extends StatelessWidget {
  const _SingleStaticImage({required this.imageUrl, this.caption});

  final String imageUrl;
  final String? caption;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Column(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(12.0),
            child: _buildSingleImage(imageUrl),
          ),
        ],
      ),
    );
  }
}

class _LoadingPlaceholder extends StatelessWidget {
  const _LoadingPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 250,
      margin: const EdgeInsets.all(8.0),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest.withOpacity(0.5),
        borderRadius: BorderRadius.circular(12.0),
      ),
      child: const Center(child: CircularProgressIndicator()),
    );
  }
}

class _ErrorPlaceholder extends StatelessWidget {
  const _ErrorPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 250,
      margin: const EdgeInsets.all(8.0),
      child: const Center(child: Text('画像の読み込みに失敗しました')),
    );
  }
}

Widget _buildSingleImage(String imageUrl) {
  return CachedNetworkImage(
    imageUrl: imageUrl,
    fit: BoxFit.cover,
    width: double.infinity,
    placeholder: (context, url) =>
        const Center(child: CircularProgressIndicator()),
    errorWidget: (context, url, error) => const Center(
      child: Icon(Icons.error_outline, size: 48, color: Colors.grey),
    ),
  );
}
