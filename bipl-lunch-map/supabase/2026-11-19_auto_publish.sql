-- 2026-11-19 변경: 후기를 승인 없이 바로 공개 (reviews.sql을 실행한 뒤에 한 번만 실행)
-- Supabase 대시보드 → SQL Editor에 통째로 붙여 넣고 Run

-- 1) 새 후기는 기본으로 공개(approved = true)
alter table public.reviews alter column approved set default true;

-- 2) 방문자(anon) 쓰기 정책: 공개 상태(approved = true)로만 들어가게 바꾼다
--    (방문자는 approved 칸을 직접 정할 수 없어서 항상 기본값 true로 들어간다)
drop policy if exists "anon_insert_unapproved" on public.reviews;
create policy "anon_insert_approved" on public.reviews
  for insert to anon
  with check (approved = true);

-- 3) 읽기 정책은 그대로: approved = true 인 후기만 보인다
--    → 관리자가 Table Editor에서 approved 를 false 로 바꾸면 그 후기는 숨겨진다
-- 4) 수정·삭제: 방문자에게 권한도 정책도 없으므로 그대로 불가
