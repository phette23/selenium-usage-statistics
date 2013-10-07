#! /usr/bin/env python
from selenium import webdriver
import json
from time import sleep

cred = json.load( open( 'logins.json' ) )


def main():
  get_ebsco()
  get_proquest()
  get_gale()


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
  options = browser.find_element_by_css_selector( '#reportType' )
  for option in options.find_elements_by_tag_name( 'option' ):
    if option.get_attribute( 'value' ) == 'COUNTER Journal Report 1':
      option.click()

  # TODO: choose right month
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


main()
