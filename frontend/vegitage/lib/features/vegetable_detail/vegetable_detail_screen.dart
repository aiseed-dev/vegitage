// vegetable_detail_screen.dart
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:flutter/rendering.dart';
import 'package:share_plus/share_plus.dart';
import 'package:vegitage/core/models/vegetable.dart';
import 'package:vegitage/core/providers/providers.dart';
import 'package:vegitage/shared/constants/app_strings.dart';
import 'package:vegitage/features/vegetable_detail/widgets/image_carousel_section.dart';

class VegetableDetailScreen extends StatefulWidget {
  final String vegetableId;

  const VegetableDetailScreen({super.key, required this.vegetableId});

  @override
  State<VegetableDetailScreen> createState() => _VegetableDetailScreenState();
}

class _VegetableDetailScreenState extends State<VegetableDetailScreen> {
  Vegetable? _vegetable;
  bool _isLoading = true;
  String? _error;
  bool _hasCheckedRedirect = false;

  @override
  void initState() {
    super.initState();
    _checkRedirectAndLoadData();
  }

  Future<void> _checkRedirectAndLoadData() async {
    // リダイレクトチェック
    final redirectTo = await vegetableService.getRedirectTarget(widget.vegetableId);
    if (redirectTo != null && mounted) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        context.replace('/vegetables/$redirectTo');
      });
      return;
    }

    _hasCheckedRedirect = true;
    await _loadVegetable();
  }

  Future<void> _loadVegetable() async {
    try {
      final vegetable = await vegetableService.getVegetableById(widget.vegetableId);
      if (mounted) {
        setState(() {
          _vegetable = vegetable;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return _buildErrorView(context, _error!);
    }

    if (_vegetable == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final veg = _vegetable!;
    final jaContent = veg.content.ja;
    final globalInfo = veg.globalInfo;
    final bool hasImages = globalInfo.hasImages ?? false;

    return Scaffold(
      appBar: AppBar(
        title: Text(jaContent.displayName),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (hasImages)
              ImageCarouselSection(
                hasImages: hasImages,
                imageId: globalInfo.url,
                imageCategory: 'vegetable',
              ),
            _IntroductionSection(content: jaContent),
            _SectionWidget(
              title: AppStrings.sectionTitlePracticalTips,
              oneliner: jaContent.practicalOneliner,
              content: jaContent.practicalTips,
            ),
            _SectionWidget(
              title: AppStrings.sectionTitleNutrition,
              oneliner: jaContent.nutritionOneliner,
              content: jaContent.nutritionBenefits,
            ),
            _SectionWidget(
              title: AppStrings.sectionTitleHonestAssessment,
              oneliner: jaContent.honestOneliner,
              content: jaContent.honestAssessment,
            ),
            _SectionWidget(
              title: AppStrings.sectionTitleCulturalBackground,
              content: jaContent.culturalBackground,
            ),
            _SectionWidget(
              title: AppStrings.sectionTitleSafetyNotes,
              oneliner: jaContent.safetyOneliner,
              content: jaContent.safetyNotes,
            ),
            const SizedBox(height: 40),
            _QrCodeSection(vegetableId: globalInfo.url),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView(BuildContext context, String error) {
    return Scaffold(
      appBar: AppBar(title: const Text(AppStrings.errorTitle)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text('データの読み込みに失敗しました:\n$error'),
        ),
      ),
    );
  }
}

/// 導入部分（oneliner と description）を表示する専用ウィジェット
class _IntroductionSection extends StatelessWidget {
  const _IntroductionSection({required this.content});
  final ContentJa content;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            content.oneliner,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          Text(
            content.description,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.6),
          ),
        ],
      ),
    );
  }
}

/// 各セクションのUIを生成する再利用可能なウィジェット
class _SectionWidget extends StatelessWidget {
  const _SectionWidget({
    required this.title,
    required this.content,
    this.oneliner,
  });

  final String title;
  final String? oneliner;
  final String content;

  @override
  Widget build(BuildContext context) {
    if ((oneliner == null || oneliner!.isEmpty) && content.isEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const Divider(thickness: 1, height: 24),
          if (oneliner != null && oneliner!.isNotEmpty) ...[
            Text(
              '"$oneliner"',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontStyle: FontStyle.italic,
                    color: Theme.of(context).colorScheme.secondary,
                  ),
            ),
            const SizedBox(height: 12),
          ],
          if (content.isNotEmpty)
            Text(
              content,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5),
            ),
        ],
      ),
    );
  }
}

class _QrCodeSection extends StatefulWidget {
  const _QrCodeSection({required this.vegetableId});
  final String vegetableId;

  @override
  State<_QrCodeSection> createState() => _QrCodeSectionState();
}

class _QrCodeSectionState extends State<_QrCodeSection> {
  final GlobalKey _qrKey = GlobalKey();

  Future<void> _shareQrCode() async {
    try {
      RenderRepaintBoundary boundary =
          _qrKey.currentContext!.findRenderObject() as RenderRepaintBoundary;
      ui.Image image = await boundary.toImage(pixelRatio: 3.0);
      ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData == null) {
        throw Exception("Failed to convert widget to image data.");
      }
      final Uint8List pngBytes = byteData.buffer.asUint8List();

      final xFile = XFile.fromData(
        pngBytes,
        name: '${widget.vegetableId}_qr.png',
        mimeType: 'image/png',
      );

      await Share.shareXFiles(
        [xFile],
        text: '${widget.vegetableId} - Vegitage QRコード',
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('QRコードの共有に失敗しました: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final String qrData = "https://aiseed.page/#/vegetables/${widget.vegetableId}";

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 24.0),
      child: Center(
        child: Column(
          children: [
            RepaintBoundary(
              key: _qrKey,
              child: Container(
                padding: const EdgeInsets.all(12.0),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16.0),
                ),
                child: QrImageView(
                  data: qrData,
                  version: QrVersions.auto,
                  size: 180.0,
                  gapless: false,
                ),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _shareQrCode,
              icon: const Icon(Icons.share),
              label: const Text('QRコードを共有/保存'),
            ),
            const SizedBox(height: 16),
            Text(
              qrData,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
