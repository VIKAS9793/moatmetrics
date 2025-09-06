# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-09-06
### Added
- Streamlit-based demo UI for MoatMetrics
- API health check endpoint
- Configuration for API timeouts
- Error handling for API responses
- AI/ML Features:
  - Predictive analytics for client churn prediction
  - Trend analysis with historical pattern recognition
  - Industry benchmarking metrics
  - Automated anomaly detection in client data
  - Natural language explanations for insights

### Changed
- Increased API call timeouts:
  - GET requests: 10s → 30s
  - POST requests: 30s → 60s
- Improved error messages in the UI
- Updated documentation for new features
- Enhanced analytics engine with machine learning capabilities
- Improved data processing pipeline for better ML model performance

### Fixed
- Resolved model info serialization in /api/ai/health endpoint
- Fixed connection issues between Streamlit frontend and FastAPI backend
- Addressed timeout-related errors in API communication
- Fixed data preprocessing for ML model training
- Resolved issues with feature engineering pipeline

## [0.1.0] - 2025-09-04
### Added
- Initial release
- Basic project structure
- Core functionality implementation

## [0.1.0] - 2025-09-04
### Added
- Initial release
- Basic project structure
- Core functionality implementation
