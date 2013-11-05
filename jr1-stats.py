#! /usr/bin/env python
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import json
from time import sleep
import datetime

cred = json.load( open( 'logins.json' ) )
today = datetime.date.today()


def main():
  get_ebsco()
  get_proquest()
  get_gale()
  get_newsbank()


def sign_in( browser, vendor, selectors ):
  """
  selectors is a dict of three elements which match up
  with the username (un), password (pw), & submit elements
  on the vendor's admin login page
  """
  find = browser.find_element_by_css_selector
  find( selectors[ 'un' ] ).send_keys( cred[ vendor ][ 'username' ] )
  find( selectors[ 'pw' ] ).send_keys( cred[ vendor ][ 'password' ] )
  find( selectors[ 'submit' ] ).click()


def get_ebsco():
  browser = webdriver.Firefox()
  url = 'http://eadmin.ebscohost.com/EAdmin/'
  browser.get( url )

  sign_in( browser, 'ebsco', {
    'un': '#UserName',
    'pw': '#Password',
    'submit': '#Submit'
    } )

  # COUNTER reports
  browser.get( url + 'Reports/SelectCounterReportsForm.aspx' )

  browser.find_element_by_css_selector( '#showReportButton' ).click()


def get_proquest():
  browser = webdriver.Firefox()
  url = 'http://admin.proquest.com/'
  browser.get( url )

  sign_in( browser, 'proquest', {
    'un': '#username',
    'pw': '#password',
    'submit': '#submit_0'
    } )

  # Request usage reports
  browser.get( url + 'requestusagereports' )

  # choose correct report type
  reports = Select( browser.find_element_by_css_selector( '#reportType' ) )
  reports.select_by_visible_text( 'COUNTER Journal Report 1' )

  # Need to get date in format 'Nov 2013' where month is last month
  last_month = today.replace( day=1 ) - datetime.timedelta( days=1 )
  last_month = last_month.strftime( '%b %Y' )

  # set report time range
  fromMonths = Select( browser.find_element_by_css_selector( '#usagePeriodFromValue' ) )
  fromMonths.select_by_visible_text( last_month )
  # optionally, set To month to same
  #toMonths = Select( browser.find_element_by_css_selector( '#usagePeriodToValue' ) )
  #toMonths.select_by_visible_text( last_month )

  browser.find_element_by_css_selector( '#submitUsageReport' ).click()


def get_gale():
  browser = webdriver.Firefox()
  url = 'http://admin.galegroup.com/galeadmin/login.gale'
  browser.get( url )

  sign_in( browser, 'gale', {
    'un': '#user',
    'pw': '#password',
    'submit': '#login'
    } )

  # get to Reports page
  # ...plain text username & password over HTTP in a query string, seriously Gale?
  browser.get( 'http://usagereports.galegroup.com/cognos8/cgi-bin/cognos.cgi?CAMUsername=' + cred[ 'gale' ][ 'username' ] + '&CAMPassword=' + cred[ 'gale' ][ 'password' ] )

  # this method is a savior in this situation with no meaningful IDs or classes
  browser.find_element_by_link_text( 'COUNTER - Journal Report 1' ).click()

  # opens new window
  old_window = browser.current_window_handle
  for handle in browser.window_handles:
    if handle == old_window:
      # we don't need this one anymore
      browser.close()
    elif handle != old_window:
      # this one will run the report
      browser.switch_to_window( handle )

  # wait for load, takes a while
  while ( len( browser.find_elements_by_tag_name( 'button' ) ) <= 1 ):
    sleep( 1 )

  # hit "Finish" button, last of 3 here
  browser.find_elements_by_tag_name( 'button' )[ 2 ].click()


def get_newsbank():
  browser = webdriver.Firefox()
  url = 'http://stats.newsbank.com/'
  browser.get( url )

  # usage stats are IP authenticated, no login necessary but only works from on-campus
  # go to COUNTER reports
  browser.find_element_by_link_text( 'COUNTER' ).click()
  # defaults to JR1, we're done here


main()
