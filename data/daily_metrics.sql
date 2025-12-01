WITH base AS (
  SELECT
    event_date,
    country,
    platform,
    COUNT(DISTINCT user_id) AS dau,
    SUM(iap_revenue) AS total_iap_revenue,
    SUM(ad_revenue) AS total_ad_revenue,
    SUM(match_start_count) AS matches_started,
    SUM(match_end_count) AS matches_ended,
    SUM(victory_count) AS victories,
    SUM(defeat_count) AS defeats,
    SUM(server_connection_error) AS server_errors
  FROM `mimetic-maxim-479612-j9.vertigo_analytics.raw_daily_metrics`
  GROUP BY event_date, country, platform
)

SELECT
  event_date,
  country,
  platform,
  dau,
  total_iap_revenue,
  total_ad_revenue,
  SAFE_DIVIDE(total_iap_revenue + total_ad_revenue, dau) AS arpdau,
  matches_started,
  SAFE_DIVIDE(matches_started, dau) AS match_per_dau,
  SAFE_DIVIDE(victories, matches_ended) AS win_ratio,
  SAFE_DIVIDE(defeats, matches_ended) AS defeat_ratio,
  SAFE_DIVIDE(server_errors, dau) AS server_error_per_dau
FROM base;
