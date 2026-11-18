-- 비플 점심지도 후기(별점+댓글) 테이블
-- Supabase 대시보드 → SQL Editor에 통째로 붙여 넣고 Run 하면 된다. (한 번만 실행)
-- 승인 방법: Table Editor → reviews → 해당 행의 approved 를 true 로 바꾼다.

-- 1) 테이블
create table public.reviews (
  id         uuid primary key default gen_random_uuid(),
  store_id   text not null check (char_length(store_id) between 1 and 100),   -- data.js의 가게 고정 id (예: kakao-8125665)
  nickname   text not null default '익명' check (char_length(btrim(nickname)) between 1 and 20),
  rating     int  check (rating between 1 and 5),                               -- 별점 1~5 정수, 없으면 null
  comment    text check (comment is null or char_length(btrim(comment)) between 1 and 300),  -- 댓글 300자 이하, 없으면 null
  approved   boolean not null default false,                                   -- 관리자가 true로 바꿔야 공개
  created_at timestamptz not null default now(),
  constraint reviews_rating_or_comment check (rating is not null or comment is not null)  -- 별점·댓글 중 하나는 있어야 함
);

-- 가게별 승인된 후기를 최신순으로 빨리 찾기 위한 색인
create index reviews_store_approved_idx on public.reviews (store_id, created_at desc) where approved;

-- 2) RLS(행 단위 보안) 켜기: 아래 정책에 맞는 행만 읽고 쓸 수 있다
alter table public.reviews enable row level security;

-- 3) 권한: 방문자(anon)는 읽기·쓰기만, 수정·삭제 권한 자체를 주지 않는다
revoke all on public.reviews from anon, authenticated;
grant select on public.reviews to anon;
grant insert (store_id, nickname, rating, comment) on public.reviews to anon;  -- id·approved·created_at은 방문자가 정할 수 없음

-- 4) 정책
-- 읽기: 승인된 후기만 서버에서 내려간다 (승인 전 후기는 anon 키로 조회해도 안 나옴)
create policy "anon_select_approved" on public.reviews
  for select to anon
  using (approved = true);

-- 쓰기: 승인 안 된 상태(approved = false)로만 넣을 수 있다
create policy "anon_insert_unapproved" on public.reviews
  for insert to anon
  with check (approved = false);

-- UPDATE·DELETE 정책은 만들지 않는다 → RLS가 켜져 있으므로 anon은 수정·삭제 불가
